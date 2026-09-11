#!/usr/bin/env python3
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

GRID_XZ_LDU = 10.0
PLATE_HEIGHT_LDU = 8.0
BRICK_HEIGHT_LDU = 24.0
TOL = 1e-6

_BASIC_RECT_RE = re.compile(r"^(Brick|Plate)\s+(\d+)\s*x\s*(\d+)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class BasicProfile:
    width_ldu: float
    height_ldu: float
    depth_ldu: float
    kind: str


def infer_basic_profile(description: str) -> BasicProfile | None:
    normalized = " ".join(description.split())
    m = _BASIC_RECT_RE.match(normalized)
    if not m:
        return None
    kind, a, b = m.groups()
    height = BRICK_HEIGHT_LDU if kind.lower() == "brick" else PLATE_HEIGHT_LDU
    return BasicProfile(float(int(a) * 20), height, float(int(b) * 20), kind.lower())


def _is_multiple(value: float, step: float) -> bool:
    return abs(value / step - round(value / step)) <= TOL


def _signed_permutation(matrix: list[Any]) -> bool:
    if len(matrix) != 9:
        return False
    m = [[float(matrix[r * 3 + c]) for c in range(3)] for r in range(3)]
    for row in m:
        if sum(abs(v) > TOL for v in row) != 1:
            return False
        if not any(abs(abs(v) - 1.0) <= TOL for v in row):
            return False
    for c in range(3):
        col = [m[r][c] for r in range(3)]
        if sum(abs(v) > TOL for v in col) != 1:
            return False
    return True


def _world_sizes(profile: BasicProfile, rotation: list[Any]) -> tuple[float, float, float]:
    local = (profile.width_ldu, profile.height_ldu, profile.depth_ldu)
    m = [[float(rotation[r * 3 + c]) for c in range(3)] for r in range(3)]
    return tuple(sum(abs(m[r][c]) * local[c] for c in range(3)) for r in range(3))  # type: ignore[return-value]


def _bbox(profile: BasicProfile, placement: dict) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    pos = placement["position"]
    sx, sy, sz = _world_sizes(profile, placement["rotation"])
    # LDraw basic bricks/plates use their top-center as origin in the common studs-up orientation.
    # For signed-permutation rotations we conservatively center non-vertical axes and let Y extend
    # from origin by the transformed size. For v1 collision checks this is intentionally limited
    # to ordinary studs-up basic parts (validated separately below).
    return (
        (float(pos["x"]) - sx / 2.0, float(pos["x"]) + sx / 2.0),
        (float(pos["y"]), float(pos["y"]) + sy),
        (float(pos["z"]) - sz / 2.0, float(pos["z"]) + sz / 2.0),
    )


def _overlap_1d(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return min(a[1], b[1]) - max(a[0], b[0]) > TOL


def _bbox_overlap(a, b) -> bool:
    return all(_overlap_1d(a[i], b[i]) for i in range(3))


def validate_geometry(model: dict, catalog: dict) -> tuple[list[dict], str]:
    findings: list[dict] = []
    unsupported = 0

    for sm_idx, sm in enumerate(model.get("submodels", [])):
        boxes: list[tuple[str, tuple]] = []
        for p_idx, part in enumerate(sm.get("parts", [])):
            path = f"submodels.{sm_idx}.parts.{p_idx}"
            entry = catalog.get("parts", {}).get(part["ldraw_part"].lower())
            if not entry:
                continue
            profile = infer_basic_profile(entry.get("description", ""))
            if profile is None:
                unsupported += 1
                findings.append({
                    "code": "GE090", "severity": "warning",
                    "message": f"No conservative v1 geometry profile for {part['ldraw_part']}; collision/grid checks skipped for this part",
                    "path": f"{path}.ldraw_part"
                })
                continue

            placement = part["placement"]
            rot = placement["rotation"]
            if not _signed_permutation(rot):
                findings.append({
                    "code": "GE101", "severity": "error",
                    "message": "Version 1 geometry permits only orthogonal 90-degree axis rotations for profiled basic parts",
                    "path": f"{path}.placement.rotation"
                })
                continue

            pos = placement["position"]
            if not _is_multiple(float(pos["x"]), GRID_XZ_LDU) or not _is_multiple(float(pos["z"]), GRID_XZ_LDU):
                findings.append({
                    "code": "GE110", "severity": "error",
                    "message": "Basic studs-up part center must align to the 10 LDU half-stud grid on X/Z",
                    "path": f"{path}.placement.position"
                })
            if not _is_multiple(float(pos["y"]), PLATE_HEIGHT_LDU):
                findings.append({
                    "code": "GE111", "severity": "error",
                    "message": "Basic brick/plate Y position must align to the 8 LDU plate-height grid",
                    "path": f"{path}.placement.position.y"
                })

            # Bounding boxes are intentionally limited to normal studs-up orientation in v1.
            identity = [1,0,0,0,1,0,0,0,1]
            if all(abs(float(rot[i]) - identity[i]) <= TOL for i in range(9)):
                boxes.append((part["instance_id"], _bbox(profile, placement)))
            else:
                unsupported += 1
                findings.append({
                    "code": "GE091", "severity": "warning",
                    "message": "Collision envelope is not evaluated for rotated basic parts in geometry v1",
                    "path": f"{path}.placement.rotation"
                })

        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                if _bbox_overlap(boxes[i][1], boxes[j][1]):
                    findings.append({
                        "code": "GE120", "severity": "error",
                        "message": f"Obvious bounding-box overlap between {boxes[i][0]} and {boxes[j][0]}",
                        "path": f"submodels.{sm_idx}.parts"
                    })

    errors = any(f["severity"] == "error" for f in findings)
    if errors:
        status = "failed"
    elif unsupported:
        status = "partial"
    else:
        status = "passed"
    return findings, status
