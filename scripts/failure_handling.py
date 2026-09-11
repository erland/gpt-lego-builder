#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


PART_CODES = {"MV310"}
GEOMETRY_CODES = {"GE101", "GE110", "GE111", "GE120"}
DIMENSION_CODES = {"MV222", "MV223", "MV400"}
STRUCTURE_CODES = {"MV200", "MV201", "MV202", "MV203", "MV204", "MV205"}
COLOR_CODES = {"MV311"}
ROTATION_CODES = {"MV220", "MV221"}


def _catalog_part_set(catalog: dict) -> set[str]:
    return {str(k).lower() for k, v in catalog.get("parts", {}).items() if v.get("usable_as_model_part", False)}


def _verified_candidate(candidates: list[str], catalog: dict) -> str | None:
    known = _catalog_part_set(catalog)
    for candidate in candidates:
        normalized = str(candidate).strip().lower()
        if normalized in known:
            return normalized
    return None


def resolve_failure(report: dict, catalog: dict, replacement_candidates: list[str] | None = None) -> dict:
    """Create a fail-closed repair plan from a model-validation report.

    This function never synthesizes part identifiers. A replacement_part can only
    be emitted if the exact candidate exists in the supplied catalog.
    """
    replacement_candidates = replacement_candidates or []
    if report.get("result") == "pass":
        return {
            "schema_version": "1.0",
            "status": "no_failure",
            "source_result": "pass",
            "actions": [],
            "delivery_allowed": True,
            "blocked_part_references": [],
            "notes": ["Ingen blockerande validering hittades."],
        }

    findings = [f for f in report.get("findings", []) if f.get("severity") == "error"]
    codes = {f.get("code") for f in findings}
    blocked_parts = []
    for f in findings:
        if f.get("code") in PART_CODES:
            path = str(f.get("path", ""))
            message = str(f.get("message", ""))
            # The handler records the evidence but does not try to parse/invent a replacement.
            blocked_parts.append(path or message)

    actions = []
    priority = 1

    if codes & PART_CODES:
        replacement = _verified_candidate(replacement_candidates, catalog)
        if replacement:
            actions.append({
                "priority": priority,
                "action": "replace_verified_part",
                "reason": "En föreslagen ersättningsdel finns uttryckligen i den auktoritativa katalogen.",
                "finding_codes": sorted(codes & PART_CODES),
                "replacement_part": replacement,
            })
            priority += 1
        else:
            actions.append({
                "priority": priority,
                "action": "simplify_section",
                "reason": "Delreferensen kan inte verifieras och ingen katalogverifierad ersättare har tillhandahållits; förenkla konstruktionen med redan verifierade delar.",
                "finding_codes": sorted(codes & PART_CODES),
            })
            priority += 1

    if codes & (GEOMETRY_CODES | ROTATION_CODES):
        actions.append({
            "priority": priority,
            "action": "change_dimensions",
            "reason": "Placering eller rotation är geometriskt ogiltig; ändra lager, dimension eller orientering i stället för att kringgå validatorn.",
            "finding_codes": sorted(codes & (GEOMETRY_CODES | ROTATION_CODES)),
        })
        priority += 1

    if codes & DIMENSION_CODES:
        actions.append({
            "priority": priority,
            "action": "simplify_section",
            "reason": "Dimension eller delbudget kan inte uppfyllas i nuvarande konstruktion; minska sektionens komplexitet.",
            "finding_codes": sorted(codes & DIMENSION_CODES),
        })
        priority += 1

    if codes & COLOR_CODES:
        actions.append({
            "priority": priority,
            "action": "remove_noncritical_detail",
            "reason": "Färgkoden är inte verifierbar; använd en kataloggiltig färg eller ta bort den icke-kritiska färgdetaljen.",
            "finding_codes": sorted(codes & COLOR_CODES),
        })
        priority += 1

    if codes & STRUCTURE_CODES:
        actions.append({
            "priority": priority,
            "action": "simplify_section",
            "reason": "Submodellstrukturen är ogiltig; bygg om till en enklare acyklisk och nåbar struktur.",
            "finding_codes": sorted(codes & STRUCTURE_CODES),
        })
        priority += 1

    # A failed model is never deliverable. The final fallback is always explicit.
    actions.append({
        "priority": priority,
        "action": "report_unverifiable",
        "reason": "Om tidigare reparationssteg inte leder till en helt passerad ny validering ska modellen rapporteras som ej verifierbar och inte levereras som färdig.",
        "finding_codes": sorted(c for c in codes if c),
    })

    return {
        "schema_version": "1.0",
        "status": "repair_planned" if len(actions) > 1 else "unverifiable",
        "source_result": "fail",
        "actions": actions,
        "delivery_allowed": False,
        "blocked_part_references": sorted(set(blocked_parts)),
        "notes": [
            "Ett nytt modellförslag måste valideras från början efter varje reparation.",
            "Ingen replacement_part får förekomma om den inte finns ordagrant i katalogen.",
        ],
    }


def validate_resolution(resolution: dict, schema: dict) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(resolution), key=lambda e: list(e.path))
    if errors:
        raise ValueError("Failure-resolution schema error: " + "; ".join(e.message for e in errors))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("catalog")
    ap.add_argument("--candidate", action="append", default=[])
    ap.add_argument("--schema", default="schemas/failure-resolution.schema.json")
    ap.add_argument("--output")
    args = ap.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    result = resolve_failure(report, catalog, args.candidate)
    validate_resolution(result, schema)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
