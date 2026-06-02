"""Edge-IO CLI."""
from __future__ import annotations

import argparse
import json

from .campus_export import export_to_7gc, run_measurement
from .campus_profiles import list_campus_profiles, load_campus_profile
from .campus_reports import run_all_campus, write_campus_bundle


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-campus-profiles").set_defaults(func=lambda a: print("\n".join(list_campus_profiles())) or 0)
    sp = sub.add_parser("show-profile")
    sp.add_argument("site_id")
    sp.set_defaults(func=lambda a: print(json.dumps(load_campus_profile(a.site_id), indent=2)) or 0)
    rm = sub.add_parser("run-measurement")
    rm.add_argument("site_id")
    rm.add_argument("--mode", default="local-safe")
    rm.set_defaults(func=lambda a: print(json.dumps(run_measurement(a.site_id, a.mode), indent=2)) or 0)
    ex = sub.add_parser("export-to-7gc")
    ex.add_argument("site_id")
    ex.set_defaults(func=lambda a: print(export_to_7gc(a.site_id)) or 0)
    ra = sub.add_parser("run-all-campus")
    ra.add_argument("--mode", default="local-safe")
    ra.set_defaults(func=lambda a: run_all_campus(a.mode) or 0)
    pr = sub.add_parser("make-privacy-report")
    pr.add_argument("site_id")
    pr.set_defaults(func=lambda a: write_campus_bundle(a.site_id) or 0)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
