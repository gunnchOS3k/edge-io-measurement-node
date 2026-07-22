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
from .consent.lifecycle import ConsentRecord
from .contracts.validate import validate_batch
from .exporters.seven_gc_export import export_batch_to_7gc


def _cmd_collect(args: argparse.Namespace) -> int:
    consent = ConsentRecord()
    consent.acknowledge_summary()
    if not args.consent:
        raise SystemExit(
            "Refusing to collect without --consent (affirmative opt-in required)"
        )
    consent.require_opt_in(site_id=args.site, run_id=args.run_id, affirmative=True)

    session = MeasurementSession(
        run_id=args.run_id,
        site_id=args.site,
        profile=args.profile,
        duration_s=float(args.duration),
        consent=consent,
        retention_days=int(args.retention_days),
    )

    if args.collector == "physical":
        collector: DeterministicEmulatorCollector | PhysicalDeviceCollector = (
            PhysicalDeviceCollector()
        )
        evidence = "controlled_device_measurement"
    else:
        collector = DeterministicEmulatorCollector(seed=int(args.seed))
        evidence = "synthetic"

    # Physical collector raises immediately if no device is connected.
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

    if args.collector == "emulator":
        batch = collector.stop()
        # ensure evidence label remains synthetic
        assert batch.payload["evidence_level"] == evidence
    else:  # pragma: no cover - physical path blocked earlier
        batch = collector.stop()

    out = Path(args.output)
    batch.write(out)
    print(json.dumps({"wrote": str(out), "evidence_level": evidence, "n": len(session.samples)}, indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    result = validate_batch(Path(args.path), schema_dir=args.schema_dir)
    print(json.dumps(result, indent=2))
    return 0


def _cmd_export_to_7gc_file(args: argparse.Namespace) -> int:
    path = export_batch_to_7gc(
        Path(args.input),
        Path(args.output),
        schema_dir=args.schema_dir,
    )
    print(str(path))
    return 0


def _cmd_withdraw(args: argparse.Namespace) -> int:
    # Session-file based withdrawal helper for tests / local client
    path = Path(args.session)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if "consent" not in doc:
        raise SystemExit("Session file missing consent block")
    doc["consent"]["status"] = "withdrawn"
    from .consent.lifecycle import utc_now_iso

    doc["consent"]["withdrawn_at"] = utc_now_iso()
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"withdrawn": str(path)}, indent=2))
    return 0


def _cmd_delete_session(args: argparse.Namespace) -> int:
    path = Path(args.session)
    if path.exists():
        path.unlink()
    print(json.dumps({"deleted": str(path)}, indent=2))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="edge-io")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Legacy campus commands
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

    # Gate 2 commands
    collect = sub.add_parser("collect", help="Collect a measurement session")
    collect.add_argument("--profile", choices=["learn", "create", "sense"], required=True)
    collect.add_argument("--duration", type=float, default=300)
    collect.add_argument("--interval", type=float, default=30)
    collect.add_argument("--site", default="gary")
    collect.add_argument("--run-id", required=True)
    collect.add_argument("--output", required=True)
    collect.add_argument("--consent", action="store_true", help="Affirmative opt-in")
    collect.add_argument(
        "--collector",
        choices=["emulator", "physical"],
        default="emulator",
        help="emulator=synthetic; physical requires a connected device",
    )
    collect.add_argument("--seed", type=int, default=7)
    collect.add_argument("--retention-days", type=int, default=30)
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

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
