#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from ldraw_export import export_model
from model_validation import load_and_validate

TYPE1 = re.compile(r'^1\s+\d+\s+(?:-?(?:\d+(?:\.\d+)?|\.\d+)\s+){12}\S+$')


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    suite_root = root / 'examples/studio-compatibility'
    manifest = json.loads((suite_root / 'cases.json').read_text(encoding='utf-8'))
    failures: list[str] = []
    results=[]

    for case in manifest['cases']:
        model_path = suite_root / case['model']
        model, report = load_and_validate(model_path, root/'catalog/catalog.json', root, allow_fixture=True)
        if report['result'] != 'pass':
            failures.append(f"{case['id']}: validation failed: {report['findings']}")
            continue
        if report['statistics']['expanded_parts'] != case['expected_expanded_parts']:
            failures.append(f"{case['id']}: expected expanded_parts={case['expected_expanded_parts']}, got {report['statistics']['expanded_parts']}")
            continue

        with tempfile.TemporaryDirectory() as td:
            ext=case['expected_format']
            out=Path(td)/f"model.{ext}"
            fmt=export_model(model,out)
            text=out.read_text(encoding='utf-8')
            if fmt != ext:
                failures.append(f"{case['id']}: expected format {ext}, got {fmt}")
                continue
            lines=text.splitlines()
            part_lines=[ln for ln in lines if ln.startswith('1 ')]
            if not part_lines or not all(TYPE1.match(ln) for ln in part_lines):
                failures.append(f"{case['id']}: malformed or missing LDraw type-1 line")
                continue
            if ext == 'mpd':
                if '0 FILE main.ldr' not in text or '0 FILE module.ldr' not in text or '0 NOFILE' not in text:
                    failures.append(f"{case['id']}: MPD FILE/NOFILE framing is incomplete")
                    continue
            # Persist a deterministic golden export for manual Studio opening.
            golden=model_path.parent/f"model.{ext}"
            export_model(model,golden)
            results.append({
                'id':case['id'], 'format':fmt, 'expanded_parts':report['statistics']['expanded_parts'],
                'geometry':report['checks']['geometry'], 'warnings':report['statistics']['warnings'],
                'file':golden.relative_to(root).as_posix()
            })

    report_path=suite_root/'automated-results.json'
    report_path.write_text(json.dumps({'suite_version':'1.0','result':'pass' if not failures else 'fail','cases':results,'failures':failures},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if failures:
        print('Stud.io compatibility tests: FAIL')
        for f in failures: print(' -',f)
        return 1
    print(f"Stud.io compatibility tests: PASS ({len(results)} cases; file-format compatibility only, GUI import not asserted)")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
