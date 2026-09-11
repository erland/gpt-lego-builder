#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import Counter, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import jsonschema

from ldraw_catalog import load_catalog, validate_color_code, validate_part_reference
from geometry_validation import validate_geometry

ROT_TOL = 1e-6


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    path: str | None = None


def _path(parts: list[Any]) -> str:
    return ".".join(str(p) for p in parts) if parts else "<root>"


def _finite_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _validate_rotation(matrix: list[Any]) -> str | None:
    if len(matrix) != 9 or any(not _finite_number(v) for v in matrix):
        return "Rotation must contain nine finite numeric values"
    m = [[float(matrix[r * 3 + c]) for c in range(3)] for r in range(3)]
    for r in range(3):
        norm = sum(v * v for v in m[r])
        if abs(norm - 1.0) > ROT_TOL:
            return "Rotation matrix rows must be unit length"
    for r1 in range(3):
        for r2 in range(r1 + 1, 3):
            dot = sum(m[r1][c] * m[r2][c] for c in range(3))
            if abs(dot) > ROT_TOL:
                return "Rotation matrix rows must be orthogonal"
    det = (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )
    if abs(det - 1.0) > ROT_TOL:
        return "Rotation matrix must represent a proper rotation (determinant +1); scaling/reflection is not allowed in v1"
    return None


def _validate_placement(placement: dict, path: str, findings: list[Finding]) -> None:
    pos = placement.get("position", {})
    for axis in ("x", "y", "z"):
        if not _finite_number(pos.get(axis)):
            findings.append(Finding("MV220", "error", f"Position {axis} must be a finite number", f"{path}.position.{axis}"))
    err = _validate_rotation(placement.get("rotation", []))
    if err:
        findings.append(Finding("MV221", "error", err, f"{path}.rotation"))


def _expanded_part_count(root_id: str, by_id: dict[str, dict], graph: dict[str, list[str]]) -> int:
    memo: dict[str, int] = {}

    def count(sm_id: str) -> int:
        if sm_id in memo:
            return memo[sm_id]
        sm = by_id[sm_id]
        total = len(sm.get("parts", []))
        for child in graph.get(sm_id, []):
            total += count(child)
        memo[sm_id] = total
        return total

    return count(root_id)


def validate_model(model: dict, schema: dict, catalog: dict, *, allow_fixture: bool = False) -> dict:
    findings: list[Finding] = []

    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(model), key=lambda e: list(e.absolute_path))
    for err in schema_errors:
        findings.append(Finding("MV100", "error", err.message, _path(list(err.absolute_path))))

    if schema_errors:
        return _report(model, catalog, findings, schema_ok=False, catalog_ok=False, structural_ok=False, expanded_parts=None)

    if catalog.get("source", {}).get("kind") != "official_release" and not allow_fixture:
        findings.append(Finding("MV300", "error", "Catalog is not an official_release catalog; fixture catalogs are test-only", "catalog.source.kind"))

    submodels = model["submodels"]
    ids = [sm["id"] for sm in submodels]
    duplicate_ids = [k for k, n in Counter(ids).items() if n > 1]
    for sm_id in duplicate_ids:
        findings.append(Finding("MV200", "error", f"Duplicate submodel id: {sm_id}", "submodels"))
    by_id = {sm["id"]: sm for sm in submodels}
    known = set(by_id)
    root_id = ids[0]

    instance_ids: list[str] = []
    graph: dict[str, list[str]] = {sm_id: [] for sm_id in known}

    catalog_failures = False
    for sm_idx, sm in enumerate(submodels):
        sm_path = f"submodels.{sm_idx}"
        for p_idx, part in enumerate(sm.get("parts", [])):
            ppath = f"{sm_path}.parts.{p_idx}"
            instance_ids.append(part["instance_id"])
            ok, message = validate_part_reference(catalog, part["ldraw_part"])
            if not ok:
                catalog_failures = True
                findings.append(Finding("MV310", "error", message, f"{ppath}.ldraw_part"))
            ok, message = validate_color_code(catalog, part["color"])
            if not ok:
                catalog_failures = True
                findings.append(Finding("MV311", "error", message, f"{ppath}.color"))
            _validate_placement(part["placement"], f"{ppath}.placement", findings)

        for i_idx, inst in enumerate(sm.get("submodel_instances", [])):
            ipath = f"{sm_path}.submodel_instances.{i_idx}"
            instance_ids.append(inst["instance_id"])
            target = inst["submodel_id"]
            if target not in known:
                findings.append(Finding("MV201", "error", f"Unknown submodel reference: {target}", f"{ipath}.submodel_id"))
            else:
                graph[sm["id"]].append(target)
                if target == sm["id"]:
                    findings.append(Finding("MV202", "error", f"Self-referencing submodel: {target}", f"{ipath}.submodel_id"))
            color = inst.get("color", 16)
            ok, message = validate_color_code(catalog, color)
            if not ok:
                catalog_failures = True
                findings.append(Finding("MV311", "error", message, f"{ipath}.color"))
            _validate_placement(inst["placement"], f"{ipath}.placement", findings)

    for instance_id, n in Counter(instance_ids).items():
        if n > 1:
            findings.append(Finding("MV203", "error", f"Duplicate instance_id: {instance_id}", "submodels"))

    # Preferred colors are also LDraw colors, even though they are only design constraints.
    for idx, color in enumerate(model.get("requirements", {}).get("preferred_colors", [])):
        ok, message = validate_color_code(catalog, color)
        if not ok:
            catalog_failures = True
            findings.append(Finding("MV311", "error", message, f"requirements.preferred_colors.{idx}"))

    structural_blocking = any(f.code in {"MV200", "MV201", "MV202", "MV203"} for f in findings)
    cycle_found = False
    if not structural_blocking:
        state = {sm_id: 0 for sm_id in known}

        def visit(sm_id: str, trail: list[str]) -> None:
            nonlocal cycle_found
            state[sm_id] = 1
            for child in graph[sm_id]:
                if state[child] == 1:
                    cycle_found = True
                    cycle = " -> ".join(trail + [sm_id, child])
                    findings.append(Finding("MV204", "error", f"Cyclic submodel reference graph: {cycle}", "submodels"))
                elif state[child] == 0:
                    visit(child, trail + [sm_id])
            state[sm_id] = 2

        visit(root_id, [])

        if not cycle_found:
            reachable: set[str] = set()
            queue = deque([root_id])
            while queue:
                sm_id = queue.popleft()
                if sm_id in reachable:
                    continue
                reachable.add(sm_id)
                queue.extend(graph[sm_id])
            for sm_id in ids[1:]:
                if sm_id not in reachable:
                    findings.append(Finding("MV205", "error", f"Submodel is unreachable from root submodel {root_id}: {sm_id}", "submodels"))

    dimensions = model["dimensions"]
    for axis in ("x", "y", "z"):
        lo = dimensions["min"][axis]
        hi = dimensions["max"][axis]
        if not (_finite_number(lo) and _finite_number(hi)):
            findings.append(Finding("MV222", "error", f"Dimension {axis} bounds must be finite numbers", f"dimensions.{axis}"))
        elif lo > hi:
            findings.append(Finding("MV223", "error", f"Dimension min.{axis} must not exceed max.{axis}", "dimensions"))

    expanded_parts = None
    graph_blocking = any(f.code in {"MV200", "MV201", "MV202", "MV204", "MV205"} for f in findings)
    if not graph_blocking:
        expanded_parts = _expanded_part_count(root_id, by_id, graph)
        max_parts = model.get("requirements", {}).get("max_parts")
        if max_parts is not None and expanded_parts > max_parts:
            findings.append(Finding("MV400", "error", f"Expanded model has {expanded_parts} parts, exceeding max_parts={max_parts}", "requirements.max_parts"))

    placement_failures = any(f.code.startswith("MV22") for f in findings)
    structural_failures = any(f.code.startswith("MV20") or f.code == "MV400" for f in findings)
    catalog_ok = not catalog_failures and not any(f.code == "MV300" for f in findings)
    structural_ok = not structural_failures and not placement_failures

    geometry_status = "pending"
    if catalog_ok and structural_ok:
        geometry_findings, geometry_status = validate_geometry(model, catalog)
        findings.extend(Finding(**item) for item in geometry_findings)

    return _report(model, catalog, findings, schema_ok=True, catalog_ok=catalog_ok, structural_ok=structural_ok, expanded_parts=expanded_parts, geometry_status=geometry_status)


def _report(model: dict, catalog: dict, findings: list[Finding], *, schema_ok: bool, catalog_ok: bool, structural_ok: bool, expanded_parts: int | None, geometry_status: str = "pending") -> dict:
    errors = sum(f.severity == "error" for f in findings)
    warnings = sum(f.severity == "warning" for f in findings)
    return {
        "report_version": "1.0",
        "model_id": model.get("metadata", {}).get("model_id"),
        "catalog": {
            "kind": catalog.get("source", {}).get("kind"),
            "release": catalog.get("source", {}).get("release"),
            "fingerprint": catalog.get("source", {}).get("fingerprint"),
        },
        "result": "pass" if errors == 0 else "fail",
        "checks": {
            "schema": "passed" if schema_ok else "failed",
            "catalog": "passed" if catalog_ok else "failed",
            "static_structure": "passed" if structural_ok else "failed",
            "geometry": geometry_status
        },
        "statistics": {
            "errors": errors,
            "warnings": warnings,
            "findings": len(findings),
            "expanded_parts": expanded_parts,
        },
        "findings": [asdict(f) for f in findings],
        "limitations": [
            "Geometry v1 only checks basic Brick/Plate grid alignment and obvious AABB overlaps for unrotated profiled parts; it does not prove connectivity, stability, or full collision freedom.",
            "Color validation confirms an LDraw color code, not historical availability of a specific part/color combination."
        ]
    }


def load_json_strict(path: Path) -> dict:
    def reject_constant(value: str):
        raise ValueError(f"Non-standard/non-finite JSON number: {value}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def load_schema(root: Path) -> dict:
    return load_json_strict(root / "schemas/model.schema.json")


def load_and_validate(model_path: Path, catalog_path: Path, root: Path, *, allow_fixture: bool = False) -> tuple[dict, dict]:
    model = load_json_strict(model_path)
    catalog = load_catalog(catalog_path)
    return model, validate_model(model, load_schema(root), catalog, allow_fixture=allow_fixture)
