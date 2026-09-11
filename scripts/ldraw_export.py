#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path

SAFE_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$')

def fmt_num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'Non-finite/non-numeric LDraw value: {value!r}')
    if float(value).is_integer():
        return str(int(value))
    return (f'{float(value):.10f}'.rstrip('0').rstrip('.'))

def type1_line(color, placement, reference):
    p = placement['position']; r = placement['rotation']
    vals = [p['x'], p['y'], p['z'], *r]
    return '1 ' + str(int(color)) + ' ' + ' '.join(fmt_num(v) for v in vals) + ' ' + reference

def submodel_filename(submodel_id: str) -> str:
    if not SAFE_ID.fullmatch(submodel_id):
        raise ValueError(f'Unsafe submodel id: {submodel_id!r}')
    return f'{submodel_id}.ldr'

def render_submodel(sm):
    lines = [f"0 {sm['name']}", f"0 Name: {submodel_filename(sm['id'])}", '0 !LDRAW_ORG Model']
    if sm.get('description'):
        lines.append('0 // ' + sm['description'].replace('\n', ' '))
    lines.append('')
    for part in sm.get('parts', []):
        lines.append(type1_line(part['color'], part['placement'], part['ldraw_part']))
    for inst in sm.get('submodel_instances', []):
        lines.append(type1_line(inst.get('color', 16), inst['placement'], submodel_filename(inst['submodel_id'])))
    return '\n'.join(lines).rstrip() + '\n'

def validate_submodel_refs(model):
    ids = [s['id'] for s in model['submodels']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate submodel id')
    known = set(ids)
    for sm in model['submodels']:
        for inst in sm.get('submodel_instances', []):
            if inst['submodel_id'] not in known:
                raise ValueError(f"Unknown submodel reference {inst['submodel_id']!r} in {sm['id']!r}")
            if inst['submodel_id'] == sm['id']:
                raise ValueError(f"Self-referencing submodel {sm['id']!r}")

def export_model(model, output: Path, force_format=None):
    validate_submodel_refs(model)
    submodels = model['submodels']
    fmt = force_format or ('ldr' if len(submodels) == 1 and not submodels[0].get('submodel_instances') else 'mpd')
    if fmt not in {'ldr','mpd'}: raise ValueError('format must be ldr or mpd')
    if fmt == 'ldr' and len(submodels) != 1:
        raise ValueError('LDR export supports exactly one submodel; use MPD')
    if fmt == 'ldr':
        text = render_submodel(submodels[0])
    else:
        chunks=[]
        for sm in submodels:
            chunks.append(f"0 FILE {submodel_filename(sm['id'])}\n" + render_submodel(sm) + '0 NOFILE\n')
        text='\n'.join(chunks)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    return fmt

def main():
    ap=argparse.ArgumentParser(description='Export internal LEGO model JSON to LDraw LDR/MPD')
    ap.add_argument('model', type=Path); ap.add_argument('output', type=Path)
    ap.add_argument('--format', choices=['ldr','mpd'])
    a=ap.parse_args()
    model=json.loads(a.model.read_text(encoding='utf-8'))
    fmt=export_model(model,a.output,a.format)
    print(f'LDraw export: PASS ({fmt.upper()} -> {a.output})')
    return 0
if __name__=='__main__': raise SystemExit(main())
