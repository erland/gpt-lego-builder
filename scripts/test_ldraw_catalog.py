#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ldraw_catalog import build_catalog, validate_part_reference


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests/fixtures/ldraw"
    catalog = build_catalog(fixture, "fixture", "https://example.invalid/fixture", "fixture")

    assert set(catalog["parts"]) == {"3001.dat", "3003.dat"}, catalog["parts"].keys()
    assert catalog["statistics"] == {"indexed_files": 2, "usable_parts": 2, "colors": 9}
    assert catalog["parts"]["3001.dat"]["description"] == "Brick  2 x  4"
    assert validate_part_reference(catalog, "3001.dat")[0]
    assert validate_part_reference(catalog, "3001.DAT")[0]
    assert not validate_part_reference(catalog, "99999999.dat")[0]
    assert catalog["colors"]["4"]["name"] == "Red"

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        catalog_path = td / "catalog.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

        good = subprocess.run([
            sys.executable, str(root / "scripts/validate_model_catalog.py"),
            str(root / "schemas/examples/simple-table.valid.json"), str(catalog_path), "--allow-fixture"
        ], capture_output=True, text=True)
        assert good.returncode == 0, good.stdout + good.stderr

        bad = subprocess.run([
            sys.executable, str(root / "scripts/validate_model_catalog.py"),
            str(root / "tests/catalog/unknown-part.invalid.json"), str(catalog_path), "--allow-fixture"
        ], capture_output=True, text=True)
        assert bad.returncode != 0, "Unknown part must fail closed"

    print("LDraw catalog tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
