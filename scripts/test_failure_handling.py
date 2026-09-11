#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from failure_handling import resolve_failure, validate_resolution
from ldraw_catalog import build_catalog
from model_validation import load_schema, validate_model


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_no_invented_replacement(resolution: dict, catalog: dict):
    known = {k.lower() for k in catalog["parts"]}
    for action in resolution["actions"]:
        if "replacement_part" in action:
            assert action["replacement_part"].lower() in known, action


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = build_catalog(root / "tests/fixtures/ldraw", "fixture", "https://example.invalid/fixture", "fixture")
    model_schema = load_schema(root)
    resolution_schema = load(root / "schemas/failure-resolution.schema.json")

    unknown_model = load(root / "tests/catalog/unknown-part.invalid.json")
    unknown_report = validate_model(unknown_model, model_schema, catalog, allow_fixture=True)
    assert unknown_report["result"] == "fail"

    # No candidate: must simplify/abstain; must never invent an ID.
    r1 = resolve_failure(unknown_report, catalog, [])
    validate_resolution(r1, resolution_schema)
    assert r1["delivery_allowed"] is False
    assert all("replacement_part" not in a for a in r1["actions"])
    assert r1["actions"][-1]["action"] == "report_unverifiable"

    # Mixed candidates: ignore invented candidate, accept only exact catalog hit.
    r2 = resolve_failure(unknown_report, catalog, ["987654321.dat", "3003.dat"])
    validate_resolution(r2, resolution_schema)
    replacements = [a["replacement_part"] for a in r2["actions"] if a["action"] == "replace_verified_part"]
    assert replacements == ["3003.dat"], r2
    assert_no_invented_replacement(r2, catalog)

    # Only invented candidate: must not echo it as a replacement.
    r3 = resolve_failure(unknown_report, catalog, ["987654321.dat"])
    validate_resolution(r3, resolution_schema)
    assert "987654321.dat" not in json.dumps(r3)

    # Geometry failure leads to redesign and final abstention gate.
    geometry_model = load(root / "tests/geometry/overlap.invalid.json")
    geometry_report = validate_model(geometry_model, model_schema, catalog, allow_fixture=True)
    assert geometry_report["result"] == "fail"
    rg = resolve_failure(geometry_report, catalog, [])
    validate_resolution(rg, resolution_schema)
    assert any(a["action"] == "change_dimensions" for a in rg["actions"]), rg
    assert rg["actions"][-1]["action"] == "report_unverifiable"
    assert rg["delivery_allowed"] is False

    # Pass-through report permits delivery and needs no repair action.
    good_model = load(root / "schemas/examples/simple-table.valid.json")
    good_report = validate_model(good_model, model_schema, catalog, allow_fixture=True)
    assert good_report["result"] == "pass"
    ok = resolve_failure(good_report, catalog, [])
    validate_resolution(ok, resolution_schema)
    assert ok["status"] == "no_failure" and ok["delivery_allowed"] is True and ok["actions"] == []

    print("Failure handling tests: PASS (verified replacement, redesign, simplify, abstain, no invented part IDs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
