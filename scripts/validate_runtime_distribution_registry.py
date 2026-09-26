#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    registry=yaml.safe_load((ROOT/"runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    contract=yaml.safe_load((ROOT/"gpt-builder-1.5-contract.yaml").read_text(encoding="utf-8"))
    project=yaml.safe_load((ROOT/"gpt-project.yaml").read_text(encoding="utf-8"))

    if registry["builder_contract"]["target_version"]!="1.5.0":
        errors.append("registry target version must be 1.5.0")
    if registry["builder_contract"]["runtime_selection"]!="active_targets":
        errors.append("registry must select runtimes from active_targets")
    if registry["builder_contract"]["artifact_policy"]!="exact_active_target_set":
        errors.append("registry artifact policy must be exact_active_target_set")

    active=registry["active_targets"]
    planned=registry["planned_targets"]

    if active!=["chat","custom-gpt","claude","opencode"]:
        errors.append(f"active targets mismatch: {active}")
    if planned!=[]:
        errors.append(f"planned targets must be empty after adapter activation: {planned}")

    if project["runtime"]["chat_zip"].get("enabled") is not True:
        errors.append("Chat must remain enabled")
    if project["runtime"]["custom_gpt"].get("enabled") is not True:
        errors.append("Custom GPT must remain enabled")

    for rid in active:
        if registry["targets"][rid].get("status")!="active":
            errors.append(f"{rid}: status must be active")

    if registry["targets"]["chat"]["compatibility"]!="equivalent_runtime_dependent":
        errors.append("Chat compatibility mismatch")
    if registry["targets"]["custom-gpt"]["compatibility"]!="equivalent_with_platform_constraints":
        errors.append("Custom GPT compatibility mismatch")
    if registry["targets"]["claude"]["compatibility"]!="reduced":
        errors.append("Claude planned compatibility mismatch")
    if registry["targets"]["opencode"]["compatibility"]!="equivalent":
        errors.append("OpenCode planned compatibility mismatch")

    plugin=registry["inactive_targets"]["openai_plugin"]
    if plugin.get("status")!="assessment_pending":
        errors.append("OpenAI Plugin must remain assessment_pending in step 3")
    if plugin.get("compatibility")!="reduced" or plugin.get("advisory_only") is not True:
        errors.append("OpenAI Plugin baseline mismatch")

    release=registry["release"]
    if release.get("runtime_assets_from")!="active_targets":
        errors.append("release assets must derive from active_targets")
    if release.get("wildcard_runtime_selection") is not False:
        errors.append("wildcard runtime selection must remain false")
    if release.get("preserve_official_ldraw_catalog_build") is not True:
        errors.append("official LDraw catalog build must be preserved")
    if release.get("preserve_stable_release_gate") is not True:
        errors.append("stable release gate must be preserved")

    policy=contract["runtime_policy"]
    declared=set(policy["existing"].keys()) | set(policy["planned"].keys())
    if declared!=set(active):
        errors.append("normalized runtime target set differs from registry active targets")

    if errors:
        print("FAILED: GPT Builder 1.5 runtime distribution registry")
        for e in errors:
            print("-",e)
        return 1

    print("OK: GPT Builder 1.5 runtime distribution registry")
    print("Chat/Custom GPT active; Claude/OpenCode planned; release policy preserved")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
