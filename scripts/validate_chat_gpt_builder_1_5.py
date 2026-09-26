#!/usr/bin/env python3
from pathlib import Path
import argparse, zipfile, yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",required=True)
    ns=ap.parse_args()
    artifact=Path(ns.artifact)
    if not artifact.is_absolute():
        artifact=ROOT/artifact

    errors=[]
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    canonical=(ROOT/project["instructions"]["canonical"]).read_bytes()

    if not artifact.is_file():
        print(f"FAILED: Chat artifact missing: {artifact}")
        return 1

    with zipfile.ZipFile(artifact) as zf:
        names=set(zf.namelist())
        required=[
            "START-HERE.md","VERSION","MANIFEST.json","assistant/instructions.md",
            "catalog/catalog.json","catalog/source.yaml",
            "schemas/model.schema.json","schemas/construction-plan.schema.json",
            "schemas/interpreted-request.schema.json","schemas/failure-resolution.schema.json",
            "scripts/validate_model.py","scripts/export_validated_model.py",
            "scripts/model_validation.py","scripts/ldraw_export.py",
            "scripts/validate_catalog.py","scripts/runtime_self_test.py",
        ]
        for name in required:
            if name not in names:
                errors.append(f"missing Chat member: {name}")

        if "assistant/instructions.md" in names and zf.read("assistant/instructions.md")!=canonical:
            errors.append("Chat instruction is not byte-identical to canonical instruction")

        if "scripts/export_validated_model.py" in names:
            export=zf.read("scripts/export_validated_model.py").decode("utf-8")
            if 'if report["result"] != "pass"' not in export:
                errors.append("packaged export script lost fail-closed validation gate")
            if "Validated LDraw export: BLOCKED" not in export:
                errors.append("packaged export script lost explicit blocked outcome")

        if "scripts/validate_model.py" in names:
            validation=zf.read("scripts/validate_model.py").decode("utf-8")
            if 'return 0 if report["result"] == "pass" else 1' not in validation:
                errors.append("packaged validator lost blocking exit semantics")

        if "catalog/source.yaml" in names:
            source=yaml.safe_load(zf.read("catalog/source.yaml").decode("utf-8"))
            kind=(source or {}).get("kind")
            if kind=="fixture":
                # Dev/CI Chat ZIP may contain fixture catalog, but it must never claim production verification.
                instruction=zf.read("assistant/instructions.md").decode("utf-8")
                if "fixture" not in instruction or "får aldrig användas för att påstå" not in instruction:
                    errors.append("fixture catalog packaged without explicit non-production constraint")

        forbidden=("evals/","tests/","research/","build/","dist/")
        for name in names:
            if name.startswith(forbidden):
                errors.append(f"development-only content leaked into Chat ZIP: {name}")

    if errors:
        print("FAILED: Chat GPT Builder 1.5 verification")
        for e in errors: print("-",e)
        return 1

    print("OK: Chat GPT Builder 1.5 verification")
    print("Canonical instruction, catalog/schemas, deterministic validators and fail-closed export preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
