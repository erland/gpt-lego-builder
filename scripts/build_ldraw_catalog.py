#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ldraw_catalog import build_catalog

DEFAULT_URL = "https://library.ldraw.org/library/updates/complete.zip"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact verified LDraw part catalog from official library")
    parser.add_argument("source", type=Path, help="Path to complete.zip or extracted LDraw library")
    parser.add_argument("output", type=Path, help="Output JSON catalog")
    parser.add_argument("--release", required=True, help="LDraw release identifier, e.g. 2026-08")
    parser.add_argument("--canonical-url", default=DEFAULT_URL)
    parser.add_argument("--kind", choices=["official_release", "fixture"], default="official_release")
    args = parser.parse_args()

    catalog = build_catalog(args.source, args.release, args.canonical_url, args.kind)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Catalog built: {args.output}")
    print(f"Indexed files: {catalog['statistics']['indexed_files']}")
    print(f"Usable model parts: {catalog['statistics']['usable_parts']}")
    print(f"Fingerprint: {catalog['source']['fingerprint']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
