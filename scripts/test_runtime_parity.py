#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:
    raise SystemExit("PyYAML is required") from exc

FORBIDDEN_RUNTIME_PARTS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "tests", "evals", "research", "build", "dist",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".tmp", ".temp", ".swp", ".swo"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    args = ap.parse_args()
    root = Path(args.project_root).resolve()
    cfg = load_yaml(root / "gpt-project.yaml")
    registry = load_yaml(root / "runtime-distribution-registry.yaml")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    active_targets = list(registry.get("active_targets", []) or [])
    chat = root / "build" / "chat"
    custom = root / "build" / "custom-gpt"
    errors: list[str] = []
    warnings: list[str] = []

    if not chat.exists() or not custom.exists():
        print("RUNTIME PARITY: FAIL")
        print("- Build both chat and custom-gpt before parity testing")
        return 1

    chat_instr = (chat / "assistant" / "instructions.md").read_text(encoding="utf-8")
    custom_instr = (custom / "builder" / "instructions.md").read_text(encoding="utf-8")
    canonical = (root / cfg["instructions"]["canonical"]).read_text(encoding="utf-8")

    markers = list(cfg.get("instructions", {}).get("core_contract", {}).get("required_markers", []) or [])
    for marker in markers:
        for name, text in [("canonical", canonical), ("chat", chat_instr), ("custom-gpt", custom_instr)]:
            if marker not in text:
                errors.append(f"Critical behavior marker missing from {name}: {marker}")

    # Chat must carry exact canonical instructions; Custom GPT may be compiled but must preserve behavior markers.
    if digest(root / cfg["instructions"]["canonical"]) != digest(chat / "assistant" / "instructions.md"):
        errors.append("Chat instructions are not byte-identical to canonical instructions")

    chat_deps = list(cfg.get("instructions", {}).get("core_contract", {}).get("required_runtime_dependencies", []) or [])
    for rel in chat_deps:
        if not (chat / rel).exists():
            errors.append(f"Chat runtime dependency missing: {rel}")

    # Custom GPT has reference parity for schemas/catalog, while deterministic scripts are intentionally absent.
    kp = custom / "builder" / "knowledge-package"
    custom_required = [
        "catalog/catalog.json",
        "schemas/model.schema.json",
        "schemas/construction-plan.schema.json",
        "schemas/interpreted-request.schema.json",
        "schemas/failure-resolution.schema.json",
    ]
    for rel in custom_required:
        if not (kp / rel).exists():
            errors.append(f"Custom GPT critical reference missing: {rel}")

    compat = (custom / "COMPATIBILITY.md").read_text(encoding="utf-8")
    for marker in ["execution-parity", "Reducerad", "Stud.io"]:
        if marker not in compat:
            errors.append(f"Custom GPT compatibility report missing parity marker: {marker}")

    # Version and manifest parity are mandatory across every active runtime.
    runtime_roots = [(name, root / "build" / name) for name in active_targets]
    for name, runtime_root in runtime_roots:
        if not runtime_root.exists():
            errors.append(f"Active runtime build missing: {name}")
            continue
        path = runtime_root / "VERSION"
        actual = path.read_text(encoding="utf-8").strip() if path.exists() else "<missing>"
        if actual != version:
            errors.append(f"Version mismatch in {name}: {actual!r} != {version!r}")
        manifest = runtime_root / "MANIFEST.json"
        if not manifest.exists():
            errors.append(f"Manifest missing in active runtime: {name}")
        else:
            actual_manifest_version = json.loads(manifest.read_text(encoding="utf-8")).get("version")
            if actual_manifest_version != version:
                errors.append(f"Manifest version mismatch in {name}: {actual_manifest_version!r} != {version!r}")

    # Runtime packages may not leak development/test/cache artifacts.
    for runtime_name, runtime_root in runtime_roots:
        if not runtime_root.exists():
            continue
        seen_hashes: dict[str, str] = {}
        for p in runtime_root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(runtime_root)
            if any(part in FORBIDDEN_RUNTIME_PARTS for part in rel.parts):
                errors.append(f"Forbidden path in {runtime_name}: {rel}")
            if p.suffix.lower() in FORBIDDEN_SUFFIXES or p.name in {".DS_Store"}:
                errors.append(f"Temporary/cache file in {runtime_name}: {rel}")
            # Exact duplicates inside one distribution are usually accidental. Ignore manifests/version metadata.
            if p.name not in {"MANIFEST.json", "VERSION"}:
                h = digest(p)
                if h in seen_hashes:
                    warnings.append(f"Exact duplicate content in {runtime_name}: {seen_hashes[h]} == {rel}")
                else:
                    seen_hashes[h] = rel.as_posix()

    report = {
        "result": "fail" if errors else "pass",
        "version": version,
        "critical_markers": len(markers),
        "behavior_parity": "full" if not errors else "failed",
        "execution_parity": {
            name: registry["targets"][name]["compatibility"]
            for name in active_targets
        },
        "errors": errors,
        "warnings": warnings,
    }
    out = root / "build" / "runtime-parity-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("RUNTIME PARITY:", report["result"].upper())
    print(f"Behavior markers: {len(markers)}")
    print("Active runtime parity:", ", ".join(
        f"{name}={registry['targets'][name]['compatibility']}" for name in active_targets
    ))
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
