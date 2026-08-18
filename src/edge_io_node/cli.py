"""Edge-IO CLI."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .campus_export import export_to_7gc as campus_export_to_7gc
from .campus_export import run_measurement
from .campus_profiles import list_campus_profiles, load_campus_profile
from .campus_reports import run_all_campus, write_campus_bundle
from .collectors.base import (
    DeterministicEmulatorCollector,
    MeasurementSession,
    PhysicalDeviceCollector,
    delete_session,
)
from .consent.lifecycle import ConsentRecord, utc_now_iso
from .contracts.validate import validate_batch
from .exporters.seven_gc_export import export_batch_to_7gc


COLLECTION_PURPOSE_VERSION = "gate3-pilot-v1"
PRIVACY_POLICY_VERSION = "gate3-privacy-v1"


def _cmd_collect(args: argparse.Namespace) -> int:
    consent = ConsentRecord()
    consent.acknowledge_summary()
    if not args.consent:
        raise SystemExit(
            "Refusing to collect without --consent (affirmative opt-in required)"
        )
    consent.require_opt_in(site_id=args.site, run_id=args.run_id, affirmative=True)
    consent_captured_at = consent.captured_at

    session = MeasurementSession(
        run_id=args.run_id,
        site_id=args.site,
        profile=args.profile,
        duration_s=float(args.duration),
        consent=consent,
        retention_days=int(args.retention_days),
    )

    collector_mode = args.collector
    if collector_mode in {"emulator", "synthetic"}:
        print("SYNTHETIC TEST MODE", flush=True)
        collector: DeterministicEmulatorCollector | PhysicalDeviceCollector = (
            DeterministicEmulatorCollector(seed=int(args.seed))
        )
        evidence = "synthetic"
        device_category = "emulator"
    else:
        print("PHYSICAL DEVICE COLLECTION", flush=True)
        collector = PhysicalDeviceCollector(
            endpoint=args.endpoint,
            timeout_s=float(args.timeout),
            retries=int(args.retries),
            device_category=args.device_category,
            network_type=args.network_type,
        )
        evidence = "controlled_device_measurement"
        device_category = args.device_category

    start = utc_now_iso()
    collector.start(session)
    interval = max(1.0, float(args.interval))
    deadline = time.time() + float(args.duration)
    while time.time() < deadline:
        if session.consent.status == "withdrawn":
            break
        collector.sample()
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        time.sleep(min(interval, remaining))

    batch = collector.stop()
    end = utc_now_iso()
    out = Path(args.output)
    # Wrap with session context for Gate 3
    context = {
        "schema_name": "gunnchos.measurement_session_context",
        "schema_version": "1.0.0",
        "session_id": args.session_id or f"sess_{args.run_id}",
        "run_id": args.run_id,
        "collection_day_id": args.collection_day_id or "day_unassigned",
        "location_category": args.location_category,
        "named_test_zone": args.zone,
        "indoor_outdoor": args.indoor_outdoor,
        "stationary_or_moving": args.mobility,
        "network_condition": args.network_condition,
        "network_type": args.network_type,
        "workload_profile": args.profile,
        "planned_duration_seconds": float(args.duration),
        "actual_duration_seconds": float(session.elapsed_s()),
        "start_timestamp": start,
        "end_timestamp": end,
        "device_category": device_category if device_category != "emulator" else "laptop",
        "collector_version": "0.2.0-gate3",
        "consent_receipt_id": consent.receipt_id,
        "consent_captured_at": consent_captured_at,
        "collection_purpose_version": COLLECTION_PURPOSE_VERSION,
        "privacy_policy_version": PRIVACY_POLICY_VERSION,
        "environmental_notes": args.environmental_notes,
        "degradation_method": args.degradation_method,
        "operator_notes": args.operator_notes,
        "protocol_deviation": args.protocol_deviation or None,
        "evidence_level": evidence,
    }
    if evidence == "synthetic":
        # Keep device_category schema-valid for context while batch remains synthetic
        context["device_category"] = "laptop"
    wrapped = {
        "measurement_batch": batch.to_dict(),
        "session_context": context,
        "collection_mode_label": (
            "PHYSICAL DEVICE COLLECTION" if evidence == "controlled_device_measurement" else "SYNTHETIC TEST MODE"
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    # For Gate 2 pipeline compatibility, also allow writing bare batch when --bare-batch
    if args.bare_batch:
        batch.write(out)
    else:
        out.write_text(json.dumps(wrapped, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(out),
                "evidence_level": evidence,
                "mode": wrapped["collection_mode_label"],
                "n": len(session.samples),
            },
            indent=2,
        )
    )
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    batch = doc.get("measurement_batch", doc)
    result = validate_batch(batch, schema_dir=args.schema_dir)
    print(json.dumps(result, indent=2))
    return 0


def _cmd_export_to_7gc_file(args: argparse.Namespace) -> int:
    path_in = Path(args.input)
    doc = json.loads(path_in.read_text(encoding="utf-8"))
    if "measurement_batch" in doc:
        tmp = path_in.with_suffix(".batch.json")
        tmp.write_text(json.dumps(doc["measurement_batch"], indent=2) + "\n", encoding="utf-8")
        path = export_batch_to_7gc(tmp, Path(args.output), schema_dir=args.schema_dir)
        tmp.unlink(missing_ok=True)
    else:
        path = export_batch_to_7gc(path_in, Path(args.output), schema_dir=args.schema_dir)
    print(str(path))
    return 0


def _cmd_withdraw(args: argparse.Namespace) -> int:
    path = Path(args.session)
    doc = json.loads(path.read_text(encoding="utf-8"))
    batch = doc.get("measurement_batch", doc)
    if "consent" not in batch:
        raise SystemExit("Session file missing consent block")
    batch["consent"]["status"] = "withdrawn"
    batch["consent"]["withdrawn_at"] = utc_now_iso()
    if "measurement_batch" in doc:
        doc["measurement_batch"] = batch
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(batch, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"withdrawn": str(path)}, indent=2))
    return 0


def _cmd_delete_session(args: argparse.Namespace) -> int:
    path = Path(args.session)
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["deleted"] = True
        # remove file to match delete semantics
        path.unlink()
    print(json.dumps({"deleted": str(path)}, indent=2))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="edge-io")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-campus-profiles").set_defaults(
        func=lambda a: print("\n".join(list_campus_profiles())) or 0
    )
    sp = sub.add_parser("show-profile")
    sp.add_argument("site_id")
    sp.set_defaults(func=lambda a: print(json.dumps(load_campus_profile(a.site_id), indent=2)) or 0)
    rm = sub.add_parser("run-measurement")
    rm.add_argument("site_id")
    rm.add_argument("--mode", default="local-safe")
    rm.set_defaults(func=lambda a: print(json.dumps(run_measurement(a.site_id, a.mode), indent=2)) or 0)
    ex = sub.add_parser("export-to-7gc-site")
    ex.add_argument("site_id")
    ex.set_defaults(func=lambda a: print(campus_export_to_7gc(a.site_id)) or 0)
    ra = sub.add_parser("run-all-campus")
    ra.add_argument("--mode", default="local-safe")
    ra.set_defaults(func=lambda a: run_all_campus(a.mode) or 0)
    pr = sub.add_parser("make-privacy-report")
    pr.add_argument("site_id")
    pr.set_defaults(func=lambda a: write_campus_bundle(a.site_id) or 0)

    collect = sub.add_parser("collect", help="Collect a measurement session")
    collect.add_argument("--profile", choices=["learn", "create", "sense"], required=True)
    collect.add_argument("--duration", type=float, default=300)
    collect.add_argument("--interval", type=float, default=30)
    collect.add_argument("--site", default="gary")
    collect.add_argument("--run-id", required=True)
    collect.add_argument("--session-id", default=None)
    collect.add_argument("--output", required=True)
    collect.add_argument("--consent", action="store_true", help="Affirmative opt-in")
    collect.add_argument(
        "--collector",
        choices=["emulator", "synthetic", "physical"],
        default="synthetic",
        help="synthetic/emulator=labeled synthetic; physical=device probe",
    )
    collect.add_argument("--seed", type=int, default=7)
    collect.add_argument("--retention-days", type=int, default=30)
    collect.add_argument("--device-category", default="laptop", choices=["phone", "tablet", "laptop", "kiosk"])
    collect.add_argument("--zone", default="zone_a")
    collect.add_argument(
        "--location-category",
        default="library_or_community_indoor",
        choices=[
            "home_or_private_indoor",
            "library_or_community_indoor",
            "campus_or_office_indoor",
            "outdoor_stationary",
            "transit_or_mobility",
            "other_approved_test_zone",
        ],
    )
    collect.add_argument(
        "--network-condition",
        default="wifi_normal",
        choices=["wifi_normal", "cellular_normal", "wifi_degraded", "local_network_degraded"],
    )
    collect.add_argument("--network-type", default="wifi", choices=["wifi", "cellular", "ethernet", "unknown", "degraded_local"])
    collect.add_argument("--collection-day-id", default=None)
    collect.add_argument("--indoor-outdoor", default="indoor", choices=["indoor", "outdoor", "mixed"])
    collect.add_argument("--mobility", default="stationary", choices=["stationary", "moving"])
    collect.add_argument("--endpoint", default="https://www.cloudflare.com/cdn-cgi/trace")
    collect.add_argument("--timeout", type=float, default=5.0)
    collect.add_argument("--retries", type=int, default=1)
    collect.add_argument("--environmental-notes", default="")
    collect.add_argument("--degradation-method", default="none")
    collect.add_argument("--operator-notes", default="")
    collect.add_argument("--protocol-deviation", default="")
    collect.add_argument("--bare-batch", action="store_true", help="Write Gate-2 bare batch JSON only")
    collect.set_defaults(func=_cmd_collect)

    validate = sub.add_parser("validate", help="Validate a measurement batch")
    validate.add_argument("path")
    validate.add_argument("--schema-dir", default=None)
    validate.set_defaults(func=_cmd_validate)

    export = sub.add_parser("export-to-7gc", help="Validate and export batch for 7GC")
    export.add_argument("input")
    export.add_argument("--output", required=True)
    export.add_argument("--schema-dir", default=None)
    export.set_defaults(func=_cmd_export_to_7gc_file)

    wd = sub.add_parser("withdraw-consent")
    wd.add_argument("--session", required=True)
    wd.set_defaults(func=_cmd_withdraw)

    ds = sub.add_parser("delete-session")
    ds.add_argument("--session", required=True)
    ds.set_defaults(func=_cmd_delete_session)

    def _cmd_research_export(args: argparse.Namespace) -> int:
        from .research_export import export_research_pack
        from .synthetic_device_emulator import emulate_samples

        samples = emulate_samples(int(args.n))
        pack = export_research_pack(samples, site_id=args.site, out_dir=Path(args.out_dir) if args.out_dir else None)
        print(json.dumps({"wrote": pack.get("wrote"), "n": pack["n_samples"], "spatial_accuracy": pack["spatial_accuracy"]}, indent=2))
        return 0

    rexp = sub.add_parser("research-export", help="Synthetic research pack; never physical")
    rexp.add_argument("--site", default="gary")
    rexp.add_argument("--n", type=int, default=5)
    rexp.add_argument("--out-dir", default=None)
    rexp.set_defaults(func=_cmd_research_export)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
