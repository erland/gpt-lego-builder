#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
release = (root / ".github/workflows/release.yml").read_text(encoding="utf-8")
errors = []

ci_markers = [
    "python scripts/lint_gpt_project.py",
    "python scripts/run_evals.py",
    "python scripts/project_hygiene.py",
    "python scripts/build_distributions.py",
    "python scripts/validate_distributions.py",
    "python scripts/test_runtime_parity.py",
    "python scripts/verify_release_artifacts.py",
]
release_markers = [
    "workflow_dispatch:",
    "release:",
    "complete.zip",
    "--kind official_release",
    "python scripts/run_evals.py",
    "python scripts/project_hygiene.py",
    "python scripts/build_distributions.py",
    "python scripts/validate_distributions.py",
    "python scripts/test_runtime_parity.py",
    "python scripts/verify_release_artifacts.py",
    "actions/upload-artifact@v4",
    "gh release upload",
]
for marker in ci_markers:
    if marker not in ci:
        errors.append(f"CI missing required gate: {marker}")
for marker in release_markers:
    if marker not in release:
        errors.append(f"Release workflow missing requirement: {marker}")

# Guard against hard-coded release version and ensure tag/manual input is normalized.
if 'github.event.release.tag_name' not in release:
    errors.append("Release workflow does not use GitHub release tag")
if 'inputs.version' not in release:
    errors.append("Release workflow does not support manual test-release version")
if 'VERSION="${VERSION#v}"' not in release:
    errors.append("Release workflow does not normalize leading v")

if errors:
    print("CI/RELEASE WORKFLOW TEST: FAIL")
    for error in errors:
        print("-", error)
    raise SystemExit(1)
print("CI/RELEASE WORKFLOW TEST: PASS")
