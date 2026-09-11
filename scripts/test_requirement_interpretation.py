#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from interpret_requirements import interpret
catalog=json.loads((ROOT/'catalog/catalog.json').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'schemas/interpreted-request.schema.json').read_text(encoding='utf-8'))
validator=Draft202012Validator(schema)

def check(prompt, assertions):
    r=interpret(prompt,catalog)
    errs=list(validator.iter_errors(r))
    if errs: raise SystemExit('Schema fail: '+'; '.join(e.message for e in errs))
    assertions(r)

check('Bygg en liten röd traktor, ungefär 20 studs lång och max 250 delar.', lambda r: (
    (_ for _ in ()).throw(AssertionError(r)) if not (r['detail_level']=='balanced' and r['max_parts']==250 and r['target_envelope_studs']['depth']==20 and any(c['name']=='Red' for c in r['preferred_colors']) and not r['open_questions']) else None
))
check('Bygg ett enkelt svart bord, 12 x 8 x 10 studs.', lambda r: (
    (_ for _ in ()).throw(AssertionError(r)) if not (r['detail_level']=='simple' and r['target_envelope_studs']['source']=='explicit' and r['target_envelope_studs']['width']==12 and r['preferred_colors'][0]['name']=='Black') else None
))
check('Make a detailed blue display car, 24 studs long, at most 300 pieces.', lambda r: (
    (_ for _ in ()).throw(AssertionError(r)) if not (r['model_usage']=='display' and r['detail_level']=='detailed' and r['max_parts']==300 and r['target_envelope_studs']['depth']==24 and any(c['name']=='Blue' for c in r['preferred_colors'])) else None
))
check('Bygg en stuga som är 15 cm.', lambda r: (
    (_ for _ in ()).throw(AssertionError(r)) if not (len(r['open_questions'])==1 and r['open_questions'][0]['blocking'] is True) else None
))
# Missing optional values should be derived rather than triggering a question.
check('Bygg en katt.', lambda r: (
    (_ for _ in ()).throw(AssertionError(r)) if not (r['detail_level']=='balanced' and r['target_envelope_studs']['source']=='inferred' and len(r['open_questions'])==0) else None
))
print('Requirement interpretation tests: PASS')
