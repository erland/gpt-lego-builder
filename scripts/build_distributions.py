#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except Exception as exc:
    raise SystemExit("PyYAML is required to run build_distributions.py") from exc


FIXED_ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def load_config(root: Path) -> dict:
    path = root / "gpt-project.yaml"
    if not path.exists():
        raise SystemExit(f"Missing config: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_write_zip(zip_path: Path, root: Path, files: list[Path]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files, key=lambda p: p.as_posix()):
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree_filtered(src: Path, dst: Path, ignore_names: set[str] | None = None) -> None:
    # Runtime distributions must never contain local Python/cache artifacts.
    ignore_names = set(ignore_names or set()) | {
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"
    }
    if not src.exists():
        return
    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        if any(part in ignore_names for part in rel.parts):
            continue
        if p.suffix in {".pyc", ".pyo"}:
            continue
        copy_file(p, dst / rel)


def render_template(text: str, replacements: dict[str, str]) -> str:
    for k, v in replacements.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def build_manifest(root: Path, runtime_id: str, version: str, entrypoint: str | None = None) -> dict:
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "MANIFEST.json":
            files.append({
                "path": p.relative_to(root).as_posix(),
                "sha256": sha256(p),
                "size": p.stat().st_size,
            })
    result = {
        "runtime_id": runtime_id,
        "version": version,
        "files": files,
    }
    if entrypoint:
        result["entrypoint"] = entrypoint
    return result


def write_manifest(root: Path, runtime_id: str, version: str, entrypoint: str | None = None) -> None:
    manifest = build_manifest(root, runtime_id, version, entrypoint)
    (root / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_chat(root: Path, cfg: dict, build_root: Path, version: str) -> Path:
    out = build_root / "chat"
    ensure_clean_dir(out)

    assistant = out / "assistant"
    policies = assistant / "policies"
    policies.mkdir(parents=True)

    instr_src = root / cfg["instructions"]["canonical"]
    copy_file(instr_src, assistant / "instructions.md")

    starters_root = root / cfg["structure"]["conversation_starters"]["path"]
    if starters_root.exists():
        starters = [p for p in starters_root.rglob("*") if p.is_file() and p.name != "README.md"]
        if starters:
            combined = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted(starters))
            (assistant / "conversation-starters.md").write_text(combined, encoding="utf-8")

    policy_root = root / cfg["structure"]["runtime_policy"]["path"]
    if policy_root.exists():
        for p in sorted(policy_root.rglob("*.md")):
            copy_file(p, policies / p.name)

    knowledge_root = root / cfg["knowledge_architecture"]["canonical_root"]
    if knowledge_root.exists():
        for p in sorted(knowledge_root.rglob("*")):
            if p.is_file() and p.name != "KNOWLEDGE.md":
                copy_file(p, out / "knowledge" / p.relative_to(knowledge_root))

    # Chat runtime is intentionally self-contained and minimal. Canonical runtime
    # dependencies are copied explicitly so development-only tests/build tooling do
    # not leak into the portable distribution.
    runtime_docs = [
        "docs/construction-strategy.md",
        "docs/requirement-interpretation.md",
        "docs/static-validation.md",
        "docs/geometry-validation.md",
        "docs/failure-handling.md",
        "docs/ldraw-export.md",
        "docs/studio-compatibility.md",
    ]
    for rel in runtime_docs:
        src = root / rel
        if src.exists():
            copy_file(src, out / rel)

    schema_root = root / cfg["structure"]["schemas"]["path"]
    if schema_root.exists():
        for p in sorted(schema_root.glob("*.json")):
            copy_file(p, out / "schemas" / p.name)

    runtime_scripts = [
        "requirements.txt",
        "ldraw_catalog.py",
        "geometry_validation.py",
        "model_validation.py",
        "ldraw_export.py",
        "export_validated_model.py",
        "validate_model.py",
        "validate_catalog.py",
        "build_ldraw_catalog.py",
        "interpret_requirements.py",
        "failure_handling.py",
        "runtime_self_test.py",
    ]
    script_root = root / cfg["structure"]["scripts"]["path"]
    for name in runtime_scripts:
        src = script_root / name
        if src.exists():
            copy_file(src, out / "scripts" / name)

    catalog_root = root / cfg["structure"]["catalog"]["path"]
    for name in ["catalog.json", "source.yaml"]:
        src = catalog_root / name
        if src.exists():
            copy_file(src, out / "catalog" / name)

    runtime_doc = root / "docs/chat-runtime.md"
    if runtime_doc.exists():
        copy_file(runtime_doc, out / "RUNTIME.md")

    template_path = root / cfg["runtime"]["chat_zip"]["start_here_template"]
    template = template_path.read_text(encoding="utf-8")
    start_here = render_template(template, {
        "GPT_NAME": cfg["project"]["name"],
        "VERSION": version,
    })
    (out / "START-HERE.md").write_text(start_here, encoding="utf-8")
    (out / "VERSION").write_text(version + "\n", encoding="utf-8")
    write_manifest(out, cfg["project"]["id"] + "-chat", version, "START-HERE.md")
    return out


def _knowledge_priority_patterns(cfg: dict) -> list[str]:
    return list(cfg.get("knowledge_architecture", {}).get("custom_gpt", {}).get("priority", []) or [])


def _rank_knowledge(files: list[Path], root: Path, cfg: dict) -> list[Path]:
    patterns = _knowledge_priority_patterns(cfg)
    ranked = []
    for p in files:
        rel_from_project = p.relative_to(root).as_posix()
        rank = len(patterns) + 1
        for idx, pattern in enumerate(patterns):
            if fnmatch.fnmatch(rel_from_project, pattern):
                rank = idx
                break
        ranked.append((rank, rel_from_project, p))
    return [p for _, _, p in sorted(ranked)]


def collect_custom_knowledge(root: Path, cfg: dict, target: Path) -> list[Path]:
    knowledge_root = root / cfg["knowledge_architecture"]["canonical_root"]
    files = [p for p in sorted(knowledge_root.rglob("*")) if p.is_file() and p.name != "KNOWLEDGE.md"] if knowledge_root.exists() else []
    max_files = int(cfg["runtime"]["custom_gpt"]["knowledge"]["max_files"])
    strategy = cfg["runtime"]["custom_gpt"]["knowledge"]["strategy"]

    if len(files) <= max_files:
        selected = files
    elif strategy in {"prioritize", "hybrid"}:
        selected = _rank_knowledge(files, root, cfg)[:max_files]
    else:
        raise SystemExit(
            f"Custom GPT Knowledge has {len(files)} files but max is {max_files}; "
            f"strategy {strategy!r} requires explicit consolidation support for overflow."
        )

    copied = []
    for p in selected:
        dst = target / p.relative_to(knowledge_root)
        copy_file(p, dst)
        copied.append(dst)
    return copied


def compile_custom_instruction(text: str, mode: str, max_chars: int, core_markers: list[str]) -> str:
    if mode == "identical":
        compiled = text
    elif mode in {"compressed", "compiled"}:
        # Conservative deterministic compression: preserve wording and headings,
        # remove trailing whitespace and collapse repeated blank lines.
        lines = [line.rstrip() for line in text.splitlines()]
        out = []
        blank = False
        for line in lines:
            if not line.strip():
                if blank:
                    continue
                blank = True
                out.append("")
            else:
                blank = False
                out.append(line)
        compiled = "\n".join(out).strip() + "\n"
    else:
        raise SystemExit(f"Unknown Custom GPT instruction mode: {mode!r}")

    missing = [marker for marker in core_markers if marker not in compiled]
    if missing:
        raise SystemExit(f"Custom GPT instruction compilation removed core behavior markers: {missing}")
    if len(compiled) > max_chars:
        raise SystemExit(
            f"Custom GPT instruction is {len(compiled)} characters after {mode!r} compilation; max is {max_chars}. "
            "Reduce or explicitly mark distribution-specific source material; do not move core behavior to Knowledge."
        )
    return compiled


def build_custom(root: Path, cfg: dict, build_root: Path, version: str) -> Path:
    out = build_root / "custom-gpt"
    ensure_clean_dir(out)
    builder = out / "builder"
    kp = builder / "knowledge-package"
    kp.mkdir(parents=True)

    instr = (root / cfg["instructions"]["canonical"]).read_text(encoding="utf-8")
    max_chars = int(cfg["runtime"]["custom_gpt"]["instruction"]["max_characters"])
    mode = cfg["runtime"]["custom_gpt"]["instruction"]["mode"]
    core_markers = list(cfg.get("instructions", {}).get("core_contract", {}).get("required_markers", []) or [])
    compiled_instr = compile_custom_instruction(instr, mode, max_chars, core_markers)
    (builder / "instructions.md").write_text(compiled_instr, encoding="utf-8")

    starters_root = root / cfg["structure"]["conversation_starters"]["path"]
    starters = [p for p in starters_root.rglob("*") if p.is_file() and p.name != "README.md"] if starters_root.exists() else []
    combined = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted(starters))
    (builder / "conversation-starters.md").write_text(combined, encoding="utf-8")

    cap_tpl = (root / cfg["runtime"]["custom_gpt"]["templates"]["capabilities"]).read_text(encoding="utf-8")
    cap_text = render_template(cap_tpl, {
        "CAPABILITY_RECOMMENDATIONS": (
            "- **Code Interpreter & Data Analysis: PÅ (krävs)** – skapa och returnera `.ldr`/`.mpd`, samt utföra strukturerade kontroller.\n"
            "- **Web search: AV som standard** – webben får inte ersätta den auktoritativa delkatalogen.\n"
            "- **Image generation: AV som standard** – behövs inte för kärnflödet.\n"
            "- **Apps/Actions: AV i v1** – en framtida validator-Action kan ge starkare execution-parity."
        )
    })
    (builder / "capabilities.md").write_text(cap_text, encoding="utf-8")

    copied_knowledge = collect_custom_knowledge(root, cfg, kp)

    # Custom GPT Knowledge is reference material. Include the schemas and runtime
    # specifications needed to reconstruct the canonical validation flow without
    # moving behavioral rules out of builder/instructions.md.
    custom_reference_files = [
        "schemas/model.schema.json",
        "schemas/construction-plan.schema.json",
        "schemas/interpreted-request.schema.json",
        "schemas/failure-resolution.schema.json",
        "docs/construction-strategy.md",
        "docs/requirement-interpretation.md",
        "docs/static-validation.md",
        "docs/geometry-validation.md",
        "docs/failure-handling.md",
        "docs/ldraw-export.md",
        "docs/studio-compatibility.md",
    ]
    for rel in custom_reference_files:
        src = root / rel
        if src.exists():
            dst = kp / rel
            copy_file(src, dst)
            copied_knowledge.append(dst)

    # The verified part catalog is a critical runtime dependency. Bundle it as
    # one Knowledge file for Custom GPT when present. Production releases replace
    # the dev fixture with an official_release index before this build runs.
    catalog_path = root / cfg.get("structure", {}).get("catalog", {}).get("path", "catalog") / "catalog.json"
    if catalog_path.exists():
        catalog_dst = kp / "catalog" / "catalog.json"
        copy_file(catalog_path, catalog_dst)
        copied_knowledge.append(catalog_dst)

    knowledge_root = root / cfg["knowledge_architecture"]["canonical_root"]
    canonical_knowledge = [p for p in sorted(knowledge_root.rglob("*")) if p.is_file() and p.name != "KNOWLEDGE.md"] if knowledge_root.exists() else []
    selected_rel = [p.relative_to(kp).as_posix() for p in copied_knowledge]
    selected_set = set(selected_rel)
    excluded_rel = [p.relative_to(knowledge_root).as_posix() for p in canonical_knowledge if p.relative_to(knowledge_root).as_posix() not in selected_set]
    compilation_report = {
        "instruction": {
            "mode": mode,
            "canonical_characters": len(instr),
            "compiled_characters": len(compiled_instr),
            "max_characters": max_chars,
            "core_markers_verified": len(core_markers),
        },
        "knowledge": {
            "strategy": cfg["runtime"]["custom_gpt"]["knowledge"]["strategy"],
            "canonical_files": len(canonical_knowledge),
            "selected_files": len(copied_knowledge),
            "max_files": int(cfg["runtime"]["custom_gpt"]["knowledge"]["max_files"]),
            "priority_patterns": _knowledge_priority_patterns(cfg),
            "selected": selected_rel,
            "excluded": excluded_rel,
        },
    }
    (builder / "compilation-report.json").write_text(json.dumps(compilation_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme_tpl = (root / cfg["runtime"]["custom_gpt"]["templates"]["readme"]).read_text(encoding="utf-8")
    (out / "README.md").write_text(
        render_template(readme_tpl, {"GPT_NAME": cfg["project"]["name"], "VERSION": version}),
        encoding="utf-8",
    )

    compat_tpl = (root / cfg["runtime"]["custom_gpt"]["templates"]["compatibility"]).read_text(encoding="utf-8")
    compat = render_template(compat_tpl, {
        "GPT_NAME": cfg["project"]["name"],
        "RUNTIME_RECOMMENDATION": (
            "Custom GPT är ett giltigt distributionsmål när Code Interpreter & Data Analysis är aktiverat. "
            "Chat ZIP har starkare deterministisk execution-parity eftersom dess validator-script kan köras explicit."
        ),
        "PARITY_TABLE": (
            "| Förmåga | Chat ZIP | Custom GPT |\n"
            "|---|---|---|\n"
            "| Canonical beteenderegler | Full | Full |\n"
            "| Verifierad katalog som källa | Ja | Ja, som Knowledge |\n"
            "| Strukturerad krav-/modellrepresentation | Ja | Ja |\n"
            "| Deterministiska projektscript som obligatorisk gate | Ja | Reducerad |\n"
            "| Generera nedladdningsbar LDraw-fil | Ja | Ja, med Code Interpreter & Data Analysis |\n"
            "| Automatisk Stud.io GUI-verifiering | Nej | Nej |"
        ),
        "REDUCED_FEATURES": (
            "- Execution-parity är reducerad: Custom GPT kan följa samma valideringsregler, men kan inte garantera att exakt samma lokala Python-script körs som obligatorisk gate i varje konversation.\n"
            "- Knowledge-filer är referensmaterial; retrieval är inte samma sak som direkt filsystemsåtkomst till en lokal runtime.\n"
            "- En dev-build med `fixture`-katalog kan bara verifiera fixture-delarna."
        ),
        "MISSING_FEATURES": (
            "- Ingen automatisk öppning eller visuell verifiering i BrickLink Studio.\n"
            "- Ingen extern validator-Action i v1. En sådan Action är den naturliga vägen om exakt samma deterministiska server-side gate ska krävas i Custom GPT."
        ),
    })
    (out / "COMPATIBILITY.md").write_text(compat, encoding="utf-8")

    runtime_doc = root / "docs/custom-gpt-runtime.md"
    if runtime_doc.exists():
        copy_file(runtime_doc, out / "CUSTOM-GPT-RUNTIME.md")

    setup = (
        "# Preview-checklista\n\n"
        "1. Kontrollera att Code Interpreter & Data Analysis är aktiverat.\n"
        "2. Ladda upp alla Knowledge-filer.\n"
        "3. Positivt test: enkel modell med verifierade katalogdelar ska kunna ge `.ldr`.\n"
        "4. Negativt test: begär eller injicera ett okänt `.dat`-ID; GPT:n ska avstå/konstruera om.\n"
        "5. Kontrollera att GPT:n inte beskriver fixture-katalog som full produktionskatalog.\n"
        "6. Kontrollera att den inte påstår fysisk stabilitet eller full Stud.io-verifiering.\n"
    )
    (builder / "PREVIEW-CHECKLIST.md").write_text(setup, encoding="utf-8")
    (out / "VERSION").write_text(version + "\n", encoding="utf-8")

    write_manifest(out, cfg["project"]["id"] + "-custom-gpt", version)
    return out


def project_files(root: Path) -> list[Path]:
    excluded_top = {"build", "dist", ".git"}
    result = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in excluded_top:
            continue
        if "__pycache__" in rel.parts or ".pytest_cache" in rel.parts:
            continue
        result.append(p)
    return result


def write_checksums(dist: Path) -> None:
    lines = []
    for p in sorted(dist.glob("*.zip")):
        lines.append(f"{sha256(p)}  {p.name}")
    (dist / "SHA256SUMS.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_delivery_manifest(dist: Path, cfg: dict, version: str) -> None:
    artifacts = []
    for p in sorted(dist.iterdir()):
        if not p.is_file() or p.name in {"DELIVERY-MANIFEST.json"}:
            continue
        if p.suffix == ".zip":
            if "-project" in p.name:
                artifact_type = "project_zip"
            elif "-chat-" in p.name:
                artifact_type = "chat_zip"
            elif "-custom-gpt-" in p.name:
                artifact_type = "custom_gpt_zip"
            else:
                artifact_type = "zip"
        elif p.name == "SHA256SUMS.txt":
            artifact_type = "checksums"
        else:
            artifact_type = "file"
        artifacts.append({
            "type": artifact_type,
            "file": p.name,
            "sha256": sha256(p),
            "size": p.stat().st_size,
        })

    payload = {
        "project": cfg["project"]["id"],
        "project_name": cfg["project"]["name"],
        "version": version,
        "runtime_strategy": "peer_distributions",
        "custom_gpt_enabled": bool(cfg["runtime"]["custom_gpt"]["enabled"]),
        "artifacts": artifacts,
    }
    (dist / "DELIVERY-MANIFEST.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--version", default=None)
    parser.add_argument("--targets", default="project,chat,custom-gpt")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cfg = load_config(root)
    build_root = root / "build"
    dist = root / "dist"
    # Every build starts from clean generated roots so stale artifacts from an
    # earlier version can never leak into CI or a GitHub Release.
    ensure_clean_dir(build_root)
    ensure_clean_dir(dist)

    targets = {t.strip() for t in args.targets.split(",") if t.strip()}
    project_id = cfg["project"]["id"]
    if args.version:
        version = args.version.strip()
    else:
        version_file = root / "VERSION"
        if not version_file.exists():
            raise SystemExit("Missing VERSION and no --version supplied")
        version = version_file.read_text(encoding="utf-8").strip()
    if not version or any(ch.isspace() for ch in version):
        raise SystemExit(f"Invalid version: {version!r}")

    if "chat" in targets:
        chat_root = build_chat(root, cfg, build_root, version)
        chat_zip = dist / f"{project_id}-chat-{version}.zip"
        stable_write_zip(chat_zip, chat_root, [p for p in chat_root.rglob("*") if p.is_file()])

    if "custom-gpt" in targets and cfg["runtime"]["custom_gpt"]["enabled"]:
        custom_root = build_custom(root, cfg, build_root, version)
        custom_zip = dist / f"{project_id}-custom-gpt-{version}.zip"
        stable_write_zip(custom_zip, custom_root, [p for p in custom_root.rglob("*") if p.is_file()])

    if "project" in targets:
        project_zip = dist / f"{project_id}-project-{version}.zip"
        stable_write_zip(project_zip, root, project_files(root))

    write_checksums(dist)
    write_delivery_manifest(dist, cfg, version)

    print(f"Build complete: {dist}")
    for p in sorted(dist.iterdir()):
        if p.is_file():
            print(p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
