#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--project-root', default='.')
    p.add_argument('--version', required=True)
    args = p.parse_args()
    root = Path(args.project_root).resolve()
    version = args.version.strip()

    # Prereleases (rc/dev/etc.) are allowed to build without the manual GUI gate.
    if '-' in version:
        print(f'STABLE RELEASE GATE: SKIP ({version} is a prerelease)')
        return 0

    path = root / 'examples/studio-compatibility/manual-studio-results.md'
    if not path.exists():
        print('STABLE RELEASE GATE: FAIL')
        print('- Missing manual Studio verification file')
        return 1
    text = path.read_text(encoding='utf-8')
    m = re.search(r'^\*\*Status:\*\*\s*([A-Za-z0-9_-]+)\s*$', text, flags=re.M)
    status = m.group(1).lower() if m else 'missing'
    if status != 'pass':
        print('STABLE RELEASE GATE: FAIL')
        print(f'- BrickLink Studio GUI verification status is {status!r}, expected \'pass\'.')
        print('- Open every golden .ldr/.mpd case in BrickLink Studio, complete the checklist, and set **Status:** pass.')
        return 1
    if 'ej testad' in text.lower():
        print('STABLE RELEASE GATE: FAIL')
        print('- Manual Studio checklist still contains untested cells.')
        return 1
    print('STABLE RELEASE GATE: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
