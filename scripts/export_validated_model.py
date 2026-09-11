#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ldraw_export import export_model
from model_validation import load_and_validate


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Validate an internal model and export LDraw only when all static gates pass")
    ap.add_argument("model", type=Path)
    ap.add_argument("catalog", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--format", choices=["ldr", "mpd"])
    ap.add_argument("--allow-fixture", action="store_true", help="Development/tests only; never production verification")
    args = ap.parse_args()

    model, report = load_and_validate(args.model, args.catalog, root, allow_fixture=args.allow_fixture)
    if report["result"] != "pass":
        print("Validated LDraw export: BLOCKED")
        for finding in report["findings"][:20]:
            print(f" - {finding['code']}: {finding['message']}")
        return 1

    fmt = export_model(model, args.output, args.format)
    print(f"Validated LDraw export: PASS ({fmt.upper()} -> {args.output})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
