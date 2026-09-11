#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception as exc:
    raise SystemExit("jsonschema is required: pip install jsonschema") from exc


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def errors_for(validator, path: Path):
    return list(validator.iter_errors(read_json(path)))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schema = read_json(root / "schemas/model.schema.json")
    validator = jsonschema.Draft202012Validator(schema)

    valid_cases = sorted((root / "schemas/examples").glob("*.valid.json"))
    invalid_cases = sorted((root / "tests/model-schema").glob("*.invalid.json"))

    failures = []
    for path in valid_cases:
        errors = errors_for(validator, path)
        if errors:
            failures.append(f"Expected valid but failed: {path.relative_to(root)} -> {errors[0].message}")

    for path in invalid_cases:
        errors = errors_for(validator, path)
        if not errors:
            failures.append(f"Expected invalid but passed: {path.relative_to(root)}")

    if failures:
        print("Model schema tests: FAIL")
        for f in failures:
            print(" -", f)
        return 1

    print(f"Model schema tests: PASS (valid={len(valid_cases)}, invalid={len(invalid_cases)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
