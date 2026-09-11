#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile
from pathlib import Path
from ldraw_export import export_model

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def main():
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as d:
        d=Path(d)
        simple=load(root/'schemas/examples/simple-table.valid.json')
        a=d/'simple.ldr'; assert export_model(simple,a)=='ldr'
        text=a.read_text(); assert '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat' in text
        mpd=load(root/'schemas/examples/two-part-submodel.valid.json')
        b=d/'two-part.mpd'; assert export_model(mpd,b)=='mpd'
        text=b.read_text()
        assert '0 FILE main.ldr' in text and '0 FILE roof.ldr' in text
        assert '1 16 0 -24 0 1 0 0 0 1 0 0 0 1 roof.ldr' in text
        # deterministic
        c=d/'two-part-2.mpd'; export_model(mpd,c); assert b.read_bytes()==c.read_bytes()
        broken=json.loads(json.dumps(mpd)); broken['submodels'][0]['submodel_instances'][0]['submodel_id']='missing'
        try: export_model(broken,d/'bad.mpd')
        except ValueError: pass
        else: raise AssertionError('unknown submodel reference was accepted')
    print('LDraw export tests: PASS (LDR, MPD, submodel refs, deterministic output)')
    return 0
if __name__=='__main__': raise SystemExit(main())
