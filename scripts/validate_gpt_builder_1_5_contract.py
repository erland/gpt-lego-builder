#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]

def fail(errors):
    print("FAILED: GPT Builder 1.5 canonical contract normalization")
    for error in errors:
        print("-", error)
    return 1

def main():
    errors=[]
    normalized=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))
    status=yaml.safe_load((ROOT/"project-status.yaml").read_text(encoding="utf-8"))
    instruction=(ROOT/project["instructions"]["canonical"]).read_text(encoding="utf-8")
    version=(ROOT/"VERSION").read_text(encoding="utf-8").strip()
    manual=(ROOT/"examples/studio-compatibility/manual-studio-results.md").read_text(encoding="utf-8")

    if normalized["builder"]["target_version"]!="1.5.0":
        errors.append("target builder version must be 1.5.0")
    if normalized["builder"]["behavior_preserving"] is not True:
        errors.append("migration must remain behavior-preserving")
    if project["instructions"]["canonical"]!=normalized["canonical"]["instruction"]:
        errors.append("canonical instruction mismatch")

    for marker in normalized["behavior"]["required_markers"]:
        if marker not in instruction:
            errors.append(f"canonical instruction missing critical marker: {marker}")

    if normalized["behavior"]["unknown_part_ids_may_be_invented"] is not False:
        errors.append("unknown part ids must never be invented")
    if normalized["behavior"]["export_on_failed_validation"] is not False:
        errors.append("failed validation must block export")
    if normalized["behavior"]["physical_stability_claim_without_verification"] is not False:
        errors.append("unverified physical stability claim must remain forbidden")
    if normalized["behavior"]["fixture_catalog_may_claim_production_verification"] is not False:
        errors.append("fixture catalog must not claim production verification")
    if normalized["behavior"]["unrun_verification_is_pass"] is not False:
        errors.append("unrun verification must not be PASS")

    for item in normalized["contracts"]["tools"]["required"]:
        script=item.get("script")
        path=item.get("path")
        if script and not (ROOT/script).is_file():
            errors.append(f"required tool script missing: {script}")
        if path and not (ROOT/path).is_file():
            errors.append(f"required tool path missing: {path}")

    export_text=(ROOT/"scripts/export_validated_model.py").read_text(encoding="utf-8")
    if 'if report["result"] != "pass"' not in export_text:
        errors.append("fail-closed export gate not detected")
    if "Validated LDraw export: BLOCKED" not in export_text:
        errors.append("blocked export behavior not detected")

    validation_text=(ROOT/"scripts/validate_model.py").read_text(encoding="utf-8")
    if 'return 0 if report["result"] == "pass" else 1' not in validation_text:
        errors.append("blocking validator exit semantics changed")

    progress=status.get("progress",{})
    if progress.get("last_completed_step")!=18:
        errors.append("product plan must remain 18/18 complete")
    if progress.get("current_phase")!="stable-release-blocked":
        errors.append("stable-release phase must remain blocked during migration")

    if version!="1.0.0-rc.2":
        errors.append(f"VERSION changed during migration: {version!r}")

    match=re.search(r"\*\*Status:\*\*\s*([^\n]+)",manual,re.IGNORECASE)
    manual_status=match.group(1).strip() if match else None
    if manual_status!="not_run":
        errors.append(f"manual BrickLink Studio status must remain not_run, found {manual_status!r}")

    release=normalized["release_policy"]
    if release["current_version"]!="1.0.0-rc.2":
        errors.append("normalized release version mismatch")
    stable=release["stable_release"]
    if stable["status"]!="blocked":
        errors.append("stable release must remain blocked")
    if stable["manual_gate"]["current_status"]!="not_run":
        errors.append("normalized manual gate status must remain not_run")
    if stable["migration_may_set_pass"] is not False or stable["migration_may_unblock"] is not False:
        errors.append("migration must not set manual gate pass or unblock stable release")

    required_deps=set(project["instructions"]["core_contract"]["required_runtime_dependencies"])
    expected_deps={
        "schemas/model.schema.json",
        "catalog/catalog.json",
        "schemas/construction-plan.schema.json",
        "schemas/interpreted-request.schema.json",
    }
    if required_deps!=expected_deps:
        errors.append("core runtime dependency set changed")

    if errors:
        return fail(errors)

    print("OK: GPT Builder 1.5 canonical contract normalization")
    print("18/18, RC2, fail-closed export, official catalog policy and Stud.io not_run preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
