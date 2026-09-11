#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "custom-gpt"

required = [
    BUILD / "builder/instructions.md",
    BUILD / "builder/capabilities.md",
    BUILD / "builder/PREVIEW-CHECKLIST.md",
    BUILD / "builder/knowledge-package/catalog/catalog.json",
    BUILD / "builder/knowledge-package/schemas/model.schema.json",
    BUILD / "COMPATIBILITY.md",
    BUILD / "CUSTOM-GPT-RUNTIME.md",
]
missing = [str(p.relative_to(BUILD)) for p in required if not p.exists()]
assert not missing, f"missing: {missing}"

instr = (BUILD / "builder/instructions.md").read_text(encoding="utf-8")
for marker in ["VERIFIERADE DELAR ENDAST", "STUDIO-KOMPATIBEL EXPORT", "INGEN FALSK FYSIKGARANTI"]:
    assert marker in instr, marker
assert len(instr) <= 8000

cap = (BUILD / "builder/capabilities.md").read_text(encoding="utf-8")
assert "Code Interpreter & Data Analysis: PÅ" in cap
compat = (BUILD / "COMPATIBILITY.md").read_text(encoding="utf-8")
assert "execution-parity" in compat
assert "fixture" in compat

report = json.loads((BUILD / "builder/compilation-report.json").read_text(encoding="utf-8"))
assert report["instruction"]["core_markers_verified"] >= 3
assert report["knowledge"]["selected_files"] <= report["knowledge"]["max_files"]
print("Custom GPT distribution tests: PASS")
