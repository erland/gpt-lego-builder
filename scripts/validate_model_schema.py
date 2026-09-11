#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception as exc:
    raise SystemExit("jsonschema is required: pip install jsonschema") from exc


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance_path: Path) -> list[str]:
    schema = load_json(schema_path)
    instance = load_json(instance_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        loc = "/" + "/".join(str(x) for x in err.absolute_path)
        errors.append(f"{loc or '/'}: {err.message}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance")
    parser.add_argument("--schema", default="schemas/model.schema.json")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    schema = root / args.schema
    instance = Path(args.instance)
    if not instance.is_absolute():
        instance = root / instance

    errors = validate(schema, instance)
    if errors:
        print(f"FAIL: {instance}")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"PASS: {instance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
