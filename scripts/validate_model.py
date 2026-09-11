#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from model_validation import load_and_validate


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Run blocking static validation of an internal LEGO model")
    ap.add_argument("model", type=Path)
    ap.add_argument("catalog", type=Path)
    ap.add_argument("--allow-fixture", action="store_true", help="Allow fixture catalog for development/tests only")
    ap.add_argument("--report", type=Path, help="Write machine-readable JSON report")
    args = ap.parse_args()

    try:
        _, report = load_and_validate(args.model, args.catalog, root, allow_fixture=args.allow_fixture)
    except Exception as exc:
        report = {
            "report_version": "1.0",
            "model_id": None,
            "result": "fail",
            "checks": {"schema": "failed", "catalog": "failed", "static_structure": "failed", "geometry": "pending"},
            "statistics": {"errors": 1, "warnings": 0, "findings": 1, "expanded_parts": None},
            "findings": [{"code": "MV001", "severity": "error", "message": str(exc), "path": None}],
            "limitations": []
        }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Static model validation: {report['result'].upper()}")
    print(f" - schema: {report['checks']['schema']}")
    print(f" - catalog: {report['checks']['catalog']}")
    print(f" - static_structure: {report['checks']['static_structure']}")
    if report["statistics"].get("expanded_parts") is not None:
        print(f" - expanded parts: {report['statistics']['expanded_parts']}")
    for f in report.get("findings", [])[:20]:
        loc = f" [{f['path']}]" if f.get("path") else ""
        print(f" - {f['code']}: {f['message']}{loc}")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
