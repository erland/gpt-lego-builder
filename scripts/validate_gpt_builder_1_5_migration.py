#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    errors = []
    status = yaml.safe_load((ROOT / "migration-status-1.5.yaml").read_text(encoding="utf-8"))
    project = yaml.safe_load((ROOT / "project-status.yaml").read_text(encoding="utf-8"))
    registry = yaml.safe_load((ROOT / "runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manual = (ROOT / "examples/studio-compatibility/manual-studio-results.md").read_text(encoding="utf-8")
    stable = (ROOT / "docs/stable-release.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    progress = status.get("progress", {})
    if progress.get("last_completed_step") != 9:
        errors.append("migration last_completed_step must be 9")
    if progress.get("completed_steps") != list(range(1, 10)):
        errors.append("migration completed_steps must be exactly 1..9")
    if status.get("state", {}).get("overall") != "pass":
        errors.append("migration state must be pass")
    if status.get("state", {}).get("blocking_issues"):
        errors.append("migration must have no blocking issues")
    if version != "1.0.0-rc.2":
        errors.append(f"VERSION changed during migration: {version!r}")
    if project.get("progress", {}).get("last_completed_step") != 18:
        errors.append("product plan must remain 18/18 complete")
    if project.get("progress", {}).get("current_phase") != "stable-release-blocked":
        errors.append("stable release phase must remain blocked")

    match = re.search(r"\*\*Status:\*\*\s*([^\n]+)", manual, re.IGNORECASE)
    manual_status = match.group(1).strip() if match else None
    if manual_status != "not_run":
        errors.append(f"manual Stud.io status must remain not_run, found {manual_status!r}")

    if "blockerande stable-release-gate" not in stable:
        errors.append("stable-release documentation does not describe manual Studio verification as blocking")
    if "not_run" not in stable or "blockerad" not in stable:
        errors.append("stable-release documentation does not preserve current blocked/not_run state")
    if "18/18 complete" not in readme or "GPT Byggaren **1.5.0**" not in readme:
        errors.append("README migration/product status is not synchronized")

    expected_active = ["chat", "custom-gpt", "claude", "opencode"]
    if registry.get("active_targets") != expected_active:
        errors.append(f"active runtime set mismatch: {registry.get('active_targets')}")
    plugin = registry.get("inactive_targets", {}).get("openai_plugin", {})
    if plugin.get("status") != "assessed_not_active":
        errors.append("OpenAI Plugin must remain assessed_not_active")

    readiness = status.get("final_readiness", {})
    if readiness.get("migration_steps_complete") != 9 or readiness.get("migration_steps_total") != 9:
        errors.append("final readiness must declare 9/9")
    if readiness.get("stable_release_remains_blocked") is not True:
        errors.append("final readiness must preserve stable release block")

    if errors:
        print("GPT BUILDER 1.5 MIGRATION: FAIL")
        for error in errors:
            print("-", error)
        return 1

    print("GPT BUILDER 1.5 MIGRATION: PASS")
    print("9/9 complete; product 18/18 preserved; RC2 preserved; stable 1.0 remains blocked pending manual Stud.io PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
