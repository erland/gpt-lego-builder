#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ldraw_export import export_model
from model_validation import load_and_validate


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "assistant/instructions.md",
        root / "schemas/model.schema.json",
        root / "schemas/construction-plan.schema.json",
        root / "schemas/interpreted-request.schema.json",
        root / "schemas/failure-resolution.schema.json",
        root / "catalog/catalog.json",
        root / "catalog/source.yaml",
        root / "docs/construction-strategy.md",
        root / "docs/static-validation.md",
        root / "docs/failure-handling.md",
    ]
    missing = [p.relative_to(root).as_posix() for p in required if not p.exists()]
    if missing:
        print("Chat runtime self-test: FAIL")
        for rel in missing:
            print(f" - missing: {rel}")
        return 1

    catalog = json.loads((root / "catalog/catalog.json").read_text(encoding="utf-8"))
    if catalog.get("source", {}).get("kind") != "fixture":
        print("Chat runtime self-test: FAIL (expected development fixture catalog)")
        return 1

    model = {
        "schema_version": "1.0",
        "metadata": {
            "model_id": "runtime-self-test-001",
            "name": "Runtime self test",
            "description": "Portable runtime smoke test",
            "status": "draft"
        },
        "requirements": {
            "source_prompt": "Bygg en enda röd 2 x 4-kloss.",
            "design_intent": "Minsta möjliga runtime smoke test.",
            "preferred_colors": [4],
            "max_parts": 1,
            "target_dimensions_studs": {"width": 4, "depth": 2, "height": 1},
            "detail_level": "simple",
            "constraints": []
        },
        "dimensions": {
            "unit": "LDU",
            "min": {"x": -40, "y": -24, "z": -20},
            "max": {"x": 40, "y": 0, "z": 20}
        },
        "submodels": [{
            "id": "main",
            "name": "Main",
            "description": "Single verified fixture part",
            "parts": [{
                "instance_id": "p1",
                "ldraw_part": "3001.dat",
                "color": 4,
                "placement": {"position": {"x": 0, "y": 0, "z": 0}, "rotation": [1,0,0,0,1,0,0,0,1]},
                "validation": {"catalog_reference": "unverified", "placement": "unchecked", "messages": []}
            }]
        }],
        "validation": {"schema": "pending", "catalog": "pending", "geometry": "pending", "messages": []}
    }

    with tempfile.TemporaryDirectory() as td:
        model_path = Path(td) / "model.json"
        out = Path(td) / "model.ldr"
        model_path.write_text(json.dumps(model), encoding="utf-8")
        loaded, report = load_and_validate(model_path, root / "catalog/catalog.json", root, allow_fixture=True)
        if report.get("result") != "pass":
            print("Chat runtime self-test: FAIL (validation)")
            for finding in report.get("findings", [])[:10]:
                print(f" - {finding.get('code')}: {finding.get('message')}")
            return 1
        fmt = export_model(loaded, out, "ldr")
        if fmt != "ldr" or not out.exists() or "3001.dat" not in out.read_text(encoding="utf-8"):
            print("Chat runtime self-test: FAIL (export)")
            return 1

    print("Chat runtime self-test: PASS (fixture only; not production verification)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
