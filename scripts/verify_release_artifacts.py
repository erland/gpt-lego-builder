#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split(None, 1)
        result[name.strip()] = digest
    return result


def expected_zip_names(root: Path, version: str) -> set[str]:
    registry = yaml.safe_load((root / "runtime-distribution-registry.yaml").read_text(encoding="utf-8"))
    expected: set[str] = set()
    if registry.get("release", {}).get("include_project_artifact") is True:
        expected.add(registry["project_artifact"]["artifact_pattern"].format(version=version))
    for target in registry.get("active_targets", []) or []:
        entry = registry["targets"][target]
        if entry.get("status") != "active":
            raise SystemExit(f"Registry target {target!r} is listed active but status is {entry.get('status')!r}")
        expected.add(entry["artifact_pattern"].format(version=version))
    return expected


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify registry-derived release artifact set, checksums and manifest")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--version", required=True)
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    dist = root / "dist"
    expected_zips = expected_zip_names(root, args.version)
    errors: list[str] = []

    actual_zips = {p.name for p in dist.glob("*.zip")}
    missing = expected_zips - actual_zips
    extra = actual_zips - expected_zips
    if missing:
        errors.append(f"Missing release ZIPs: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected/stale release ZIPs: {sorted(extra)}")

    sums_path = dist / "SHA256SUMS.txt"
    manifest_path = dist / "DELIVERY-MANIFEST.json"
    if not sums_path.exists():
        errors.append("Missing SHA256SUMS.txt")
        sums = {}
    else:
        sums = parse_sums(sums_path)
        if set(sums) != expected_zips:
            errors.append(f"SHA256SUMS ZIP set mismatch: {sorted(sums)}")
        for name, expected in sums.items():
            target = dist / name
            if target.exists() and sha256(target) != expected:
                errors.append(f"Checksum mismatch: {name}")

    if not manifest_path.exists():
        errors.append("Missing DELIVERY-MANIFEST.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("version") != args.version:
            errors.append(f"Delivery manifest version mismatch: {manifest.get('version')!r}")
        entries = {a.get("file"): a for a in manifest.get("artifacts", [])}
        for name in expected_zips | {"SHA256SUMS.txt"}:
            if name not in entries:
                errors.append(f"Delivery manifest missing artifact: {name}")
            elif (dist / name).exists() and entries[name].get("sha256") != sha256(dist / name):
                errors.append(f"Delivery manifest digest mismatch: {name}")

    if errors:
        print("RELEASE ARTIFACTS: FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("RELEASE ARTIFACTS: PASS")
    print(f"Version: {args.version}")
    for name in sorted(expected_zips):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
