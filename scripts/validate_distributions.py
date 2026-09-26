#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except Exception as exc:
    raise SystemExit("PyYAML is required") from exc


FORBIDDEN_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "research",
    "evals",
    "tests",
}


def load_cfg(root: Path) -> dict:
    return yaml.safe_load((root / "gpt-project.yaml").read_text(encoding="utf-8"))


def validate_custom(root: Path, cfg: dict) -> list[str]:
    errors = []
    build = root / "build" / "custom-gpt"
    if not build.exists():
        return ["Custom GPT build directory missing"]

    instr = build / "builder" / "instructions.md"
    if not instr.exists():
        errors.append("Missing builder/instructions.md")
    else:
        actual = len(instr.read_text(encoding="utf-8"))
        limit = int(cfg["runtime"]["custom_gpt"]["instruction"]["max_characters"])
        if actual > limit:
            errors.append(f"Instruction too long: {actual} > {limit}")

    kp = build / "builder" / "knowledge-package"
    files = [p for p in kp.rglob("*") if p.is_file()] if kp.exists() else []
    limit = int(cfg["runtime"]["custom_gpt"]["knowledge"]["max_files"])
    if len(files) > limit:
        errors.append(f"Too many Knowledge files: {len(files)} > {limit}")

    required = [
        build / "builder" / "instructions.md",
        build / "builder" / "conversation-starters.md",
        build / "builder" / "capabilities.md",
        build / "builder" / "PREVIEW-CHECKLIST.md",
        build / "README.md",
        build / "COMPATIBILITY.md",
        build / "CUSTOM-GPT-RUNTIME.md",
        build / "VERSION",
        build / "MANIFEST.json",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"Missing required file: {p.relative_to(build)}")

    cap = build / "builder" / "capabilities.md"
    if cap.exists() and "Code Interpreter & Data Analysis: PÅ" not in cap.read_text(encoding="utf-8"):
        errors.append("Custom GPT capabilities must require Code Interpreter & Data Analysis")

    compat = build / "COMPATIBILITY.md"
    if compat.exists():
        txt = compat.read_text(encoding="utf-8")
        for marker in ["execution-parity", "fixture", "Stud.io"]:
            if marker not in txt:
                errors.append(f"Compatibility report missing marker: {marker}")

    for rel in [
        "catalog/catalog.json",
        "schemas/model.schema.json",
        "schemas/construction-plan.schema.json",
        "schemas/interpreted-request.schema.json",
        "schemas/failure-resolution.schema.json",
    ]:
        if not (kp / rel).exists():
            errors.append(f"Custom GPT Knowledge missing critical reference: {rel}")
    return errors



def validate_claude(root: Path, cfg: dict) -> list[str]:
    errors = []
    build = root / "build" / "claude"
    required = [
        build / "README.md",
        build / "VERSION",
        build / "MANIFEST.json",
        build / "project" / "instructions.md",
        build / "project" / "runtime-contract.json",
        build / "project" / "reference" / "catalog" / "catalog.json",
        build / "project" / "reference" / "schemas" / "model.schema.json",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"Missing Claude file: {p.relative_to(build)}")
    return errors


def validate_opencode(root: Path, cfg: dict) -> list[str]:
    errors = []
    build = root / "build" / "opencode"
    required = [
        build / "README.md",
        build / "VERSION",
        build / "MANIFEST.json",
        build / "AGENTS.md",
        build / "opencode.json",
        build / ".opencode" / "lego-modellbyggaren-runtime.json",
        build / ".opencode" / "runtime-scripts" / "validate_model.py",
        build / ".opencode" / "runtime-scripts" / "export_validated_model.py",
        build / "reference" / "catalog" / "catalog.json",
        build / "reference" / "schemas" / "model.schema.json",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"Missing OpenCode file: {p.relative_to(build)}")
    return errors


def validate_chat(root: Path, cfg: dict) -> list[str]:
    errors = []
    build = root / "build" / "chat"
    if not build.exists():
        return ["Chat build directory missing"]

    required = [
        build / "START-HERE.md",
        build / "VERSION",
        build / "MANIFEST.json",
        build / "assistant" / "instructions.md",
    ]
    for p in required:
        if not p.exists():
            errors.append(f"Missing required file: {p.relative_to(build)}")

    for p in build.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(build)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            errors.append(f"Forbidden runtime path: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cfg = load_cfg(root)

    errors = []
    errors.extend(validate_chat(root, cfg))
    if cfg["runtime"]["custom_gpt"]["enabled"]:
        errors.extend(validate_custom(root, cfg))
    if cfg.get("runtime", {}).get("claude", {}).get("enabled"):
        errors.extend(validate_claude(root, cfg))
    if cfg.get("runtime", {}).get("opencode", {}).get("enabled"):
        errors.extend(validate_opencode(root, cfg))

    if errors:
        print("VALIDATION: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1

    print("VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
