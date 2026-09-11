#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ldraw_catalog import load_catalog, validate_part_reference


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all model part references against a verified LDraw catalog")
    parser.add_argument("model", type=Path)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--allow-fixture", action="store_true", help="Allow non-production fixture catalog (tests only)")
    args = parser.parse_args()

    model = json.loads(args.model.read_text(encoding="utf-8"))
    catalog = load_catalog(args.catalog)
    if catalog.get("source", {}).get("kind") != "official_release" and not args.allow_fixture:
        print("Model catalog validation: FAIL")
        print(" - Catalog is not an official_release catalog; fixture catalogs are test-only")
        return 1
    failures = []
    checked = 0
    for submodel in model.get("submodels", []):
        for part in submodel.get("parts", []):
            checked += 1
            ok, message = validate_part_reference(catalog, part.get("ldraw_part", ""))
            if not ok:
                failures.append(f"{part.get('instance_id', '?')}: {message}")

    if failures:
        print("Model catalog validation: FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print(f"Model catalog validation: PASS ({checked} part references verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
