#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path


def main() -> int:
    root=Path(__file__).resolve().parents[1]
    scenario=root/'examples/end-to-end-red-tower'
    proc=subprocess.run([sys.executable,str(root/'scripts/run_reference_end_to_end.py'),'--project-root',str(root),'--allow-fixture'],capture_output=True,text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report=json.loads((scenario/'validation-report.json').read_text(encoding='utf-8'))
    assert report['result']=='pass', report
    assert report['statistics']['expanded_parts']==3, report
    ldr=(scenario/'red-tower.ldr').read_text(encoding='utf-8').splitlines()
    part_lines=[line for line in ldr if line.startswith('1 ')]
    assert len(part_lines)==3, ldr
    assert all(line.endswith('3001.dat') for line in part_lines), ldr
    assert [line.split()[3] for line in part_lines] == ['0','-24','-48'], part_lines
    assert all(line.split()[1]=='4' for line in part_lines), part_lines
    print('End-to-end tests: PASS (prompt provenance, plan schema, static gate, 3-part LDR export)')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
