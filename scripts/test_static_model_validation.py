#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ldraw_catalog import build_catalog
from model_validation import load_schema, validate_model


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = build_catalog(root / "tests/fixtures/ldraw", "fixture", "https://example.invalid/fixture", "fixture")
    schema = load_schema(root)

    for path in sorted((root / "schemas/examples").glob("*.valid.json")):
        report = validate_model(load(path), schema, catalog, allow_fixture=True)
        assert report["result"] == "pass", f"Expected PASS for {path.name}: {report}"
        assert report["checks"]["geometry"] in {"passed", "partial"}

    expected_codes = {
        "unknown-color.invalid.json": "MV311",
        "scaled-rotation.invalid.json": "MV221",
        "self-reference.invalid.json": "MV202",
        "unreachable-submodel.invalid.json": "MV205",
        "duplicate-instance.invalid.json": "MV203",
        "max-parts.invalid.json": "MV400",
        "cycle.invalid.json": "MV204",
    }
    for name, code in expected_codes.items():
        report = validate_model(load(root / "tests/static-validation" / name), schema, catalog, allow_fixture=True)
        assert report["result"] == "fail", f"Expected FAIL for {name}"
        assert code in {f["code"] for f in report["findings"]}, f"Expected {code} for {name}: {report}"

    production_gate = validate_model(load(root / "schemas/examples/simple-table.valid.json"), schema, catalog, allow_fixture=False)
    assert production_gate["result"] == "fail"
    assert "MV300" in {f["code"] for f in production_gate["findings"]}

    with tempfile.TemporaryDirectory() as td_raw:
        td = Path(td_raw)
        catalog_path = td / "catalog.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        report_path = td / "report.json"
        out = td / "model.ldr"
        good = subprocess.run([
            sys.executable, str(root / "scripts/validate_model.py"),
            str(root / "schemas/examples/simple-table.valid.json"), str(catalog_path),
            "--allow-fixture", "--report", str(report_path)
        ], capture_output=True, text=True)
        assert good.returncode == 0, good.stdout + good.stderr
        assert load(report_path)["result"] == "pass"

        exported = subprocess.run([
            sys.executable, str(root / "scripts/export_validated_model.py"),
            str(root / "schemas/examples/simple-table.valid.json"), str(catalog_path), str(out), "--allow-fixture"
        ], capture_output=True, text=True)
        assert exported.returncode == 0, exported.stdout + exported.stderr
        assert out.exists() and "3001.dat" in out.read_text(encoding="utf-8")

        blocked_out = td / "blocked.ldr"
        blocked = subprocess.run([
            sys.executable, str(root / "scripts/export_validated_model.py"),
            str(root / "tests/static-validation/unknown-color.invalid.json"), str(catalog_path), str(blocked_out), "--allow-fixture"
        ], capture_output=True, text=True)
        assert blocked.returncode != 0
        assert not blocked_out.exists(), "Blocked export must not create an output file"

    print("Static model validation tests: PASS (schema, catalog, colors, placements, graph, max-parts, export gate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
