#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def check_claude(path: Path):
    errors = []
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        for name in [
            "project/instructions.md",
            "project/runtime-contract.json",
            "project/reference/catalog/catalog.json",
            "project/reference/schemas/model.schema.json",
        ]:
            if name not in names:
                errors.append("Claude missing " + name)
        if "project/runtime-contract.json" in names:
            data = json.loads(zf.read("project/runtime-contract.json").decode("utf-8"))
            if data.get("runtime_id") != "claude_project":
                errors.append("Claude runtime_id mismatch")
            if data.get("compatibility") != "reduced":
                errors.append("Claude compatibility mismatch")
            if data.get("embedded_local_tools") is not False:
                errors.append("Claude must not claim embedded local tools")
            validation = data.get("validation", {})
            if validation.get("deterministic_scripts_embedded") is not False:
                errors.append("Claude deterministic script status mismatch")
            if validation.get("unrun_verification_is_pass") is not False:
                errors.append("Claude verification status policy mismatch")
        for name in names:
            if name.startswith("scripts/") or name.startswith(".opencode/"):
                errors.append("Claude contains runtime executable content: " + name)
    return errors

def check_opencode(path: Path):
    errors = []
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        for name in [
            "AGENTS.md",
            "opencode.json",
            ".opencode/lego-modellbyggaren-runtime.json",
            ".opencode/runtime-scripts/validate_model.py",
            ".opencode/runtime-scripts/export_validated_model.py",
            "reference/catalog/catalog.json",
            "reference/schemas/model.schema.json",
        ]:
            if name not in names:
                errors.append("OpenCode missing " + name)
        if ".opencode/lego-modellbyggaren-runtime.json" in names:
            data = json.loads(zf.read(".opencode/lego-modellbyggaren-runtime.json").decode("utf-8"))
            if data.get("runtime_id") != "opencode":
                errors.append("OpenCode runtime_id mismatch")
            if data.get("compatibility") != "equivalent":
                errors.append("OpenCode compatibility mismatch")
            if data.get("workspace_first") is not True:
                errors.append("OpenCode must be workspace-first")
            validation = data.get("validation", {})
            if validation.get("fail_closed") is not True:
                errors.append("OpenCode fail-closed validation missing")
            if validation.get("unrun_verification_is_pass") is not False:
                errors.append("OpenCode verification status policy mismatch")
        if "opencode.json" in names:
            config = json.loads(zf.read("opencode.json").decode("utf-8"))
            perm = config.get("permission", {})
            if perm.get("bash") != "ask" or perm.get("edit") != "ask":
                errors.append("OpenCode mutation permissions must require approval")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude", required=True)
    ap.add_argument("--opencode", required=True)
    ns = ap.parse_args()
    claude = Path(ns.claude)
    opencode = Path(ns.opencode)
    if not claude.is_absolute():
        claude = ROOT / claude
    if not opencode.is_absolute():
        opencode = ROOT / opencode
    errors = []
    if not claude.is_file():
        errors.append("Claude artifact missing")
    else:
        errors.extend(check_claude(claude))
    if not opencode.is_file():
        errors.append("OpenCode artifact missing")
    else:
        errors.extend(check_opencode(opencode))
    if errors:
        print("FAILED: Claude/OpenCode GPT Builder 1.5 verification")
        for error in errors:
            print("-", error)
        return 1
    print("OK: Claude reduced and OpenCode equivalent GPT Builder 1.5 verification")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
