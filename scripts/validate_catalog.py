#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate compact LDraw catalog")
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()

    schema = json.loads((root / "schemas/catalog.schema.json").read_text(encoding="utf-8"))
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(catalog), key=lambda e: list(e.path))
    if errors:
        print("Catalog validation: FAIL")
        for e in errors[:20]:
            print(" -", ".".join(map(str, e.path)) or "<root>", e.message)
        return 1
    if catalog["statistics"]["indexed_files"] != len(catalog["parts"]):
        print("Catalog validation: FAIL - indexed_files does not match parts length")
        return 1
    usable = sum(1 for p in catalog["parts"].values() if p["usable_as_model_part"])
    if catalog["statistics"]["usable_parts"] != usable:
        print("Catalog validation: FAIL - usable_parts does not match catalog entries")
        return 1
    if catalog["statistics"]["colors"] != len(catalog["colors"]):
        print("Catalog validation: FAIL - colors statistic does not match color index")
        return 1
    print(f"Catalog validation: PASS ({len(catalog['parts'])} indexed, {usable} usable, {len(catalog['colors'])} colors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
