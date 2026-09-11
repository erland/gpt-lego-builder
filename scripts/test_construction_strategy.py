#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/construction-plan.schema.json").read_text(encoding="utf-8"))
VALID = json.loads((ROOT / "schemas/examples/construction-plans/simple-table.valid.json").read_text(encoding="utf-8"))

validator = Draft202012Validator(SCHEMA)
errors = list(validator.iter_errors(VALID))
if errors:
    raise SystemExit("Valid construction plan failed schema: " + "; ".join(e.message for e in errors))

bad = json.loads(json.dumps(VALID))
bad["sections"][0]["technique"] = "free_angle_clip"
if not list(validator.iter_errors(bad)):
    raise SystemExit("Unsafe/unsupported construction technique was not rejected")

bad2 = json.loads(json.dumps(VALID))
bad2["target_envelope_studs"]["width"] = 0
if not list(validator.iter_errors(bad2)):
    raise SystemExit("Zero-width target envelope was not rejected")

expected_fallback = [
    "replace_verified_part",
    "change_dimensions",
    "simplify_section",
    "remove_noncritical_detail",
    "reduce_detail_level",
    "report_unverifiable",
]
# The schema permits a subset, but canonical strategy must document all fallbacks in order.
strategy = (ROOT / "docs/construction-strategy.md").read_text(encoding="utf-8")
positions = [strategy.find(token) for token in expected_fallback]
# Markdown uses Swedish prose, so assert the headings/rules that encode the same sequence.
required_phrases = [
    "ersätt med annan verifierad del",
    "ändra dimension eller lagerindelning",
    "förenkla den berörda sektionen",
    "ta bort icke-kritisk detalj",
    "minska detaljnivån",
    "rapportera att kravet inte kan verifieras",
]
pos = [strategy.find(p) for p in required_phrases]
if any(p < 0 for p in pos) or pos != sorted(pos):
    raise SystemExit("Canonical fallback order is missing or out of order")

print("Construction strategy tests: PASS")
