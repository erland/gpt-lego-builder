#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from ldraw_catalog import build_catalog
from model_validation import load_schema, validate_model


def load(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def main() -> int:
    root=Path(__file__).resolve().parents[1]
    catalog=build_catalog(root/'tests/fixtures/ldraw','fixture','https://example.invalid/fixture','fixture')
    schema=load_schema(root)
    valid=validate_model(load(root/'examples/end-to-end-red-tower/model.json'),schema,catalog,allow_fixture=True)
    assert valid['result']=='pass', valid
    assert valid['checks']['geometry']=='passed', valid
    expected={
        'off-grid.invalid.json':'GE110',
        'overlap.invalid.json':'GE120',
        'non-orthogonal.invalid.json':'GE101',
    }
    for name, code in expected.items():
        rep=validate_model(load(root/'tests/geometry'/name),schema,catalog,allow_fixture=True)
        assert rep['result']=='fail', (name,rep)
        assert code in {f['code'] for f in rep['findings']}, (name,rep)
        assert rep['checks']['geometry']=='failed', (name,rep)
    print('Geometry validation tests: PASS (grid, plate-height, orthogonal rotation, obvious overlap)')
    return 0

if __name__=='__main__': raise SystemExit(main())
