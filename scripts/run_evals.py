#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from interpret_requirements import interpret
from ldraw_catalog import build_catalog
from model_validation import load_schema, validate_model
from failure_handling import resolve_failure


def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    cases=load(ROOT/'evals/cases.json')['cases']
    catalog=build_catalog(ROOT/'tests/fixtures/ldraw','fixture','https://example.invalid/fixture','fixture')
    schema=load_schema(ROOT)
    results=[]
    def record(cid, ok, detail):
        case=next(c for c in cases if c['id']==cid)
        results.append({**case,'result':'pass' if ok else 'fail','detail':detail})

    # EVAL-001 unknown catalog part rejected.
    m=load(ROOT/'tests/catalog/unknown-part.invalid.json'); rep=validate_model(m,schema,catalog,allow_fixture=True)
    record('EVAL-001', rep['result']=='fail' and any(f['code']=='MV310' for f in rep['findings']), 'unknown part blocked')

    # EVAL-002 reference LDraw output type-1 syntax.
    ldr=(ROOT/'examples/end-to-end-red-tower/red-tower.ldr').read_text(encoding='utf-8').splitlines()
    part_lines=[x for x in ldr if x.startswith('1 ')]
    pat=re.compile(r'^1\s+\d+\s+-?(?:\d+(?:\.\d+)?)\s+-?(?:\d+(?:\.\d+)?)\s+-?(?:\d+(?:\.\d+)?)\s+(?:-?(?:\d+(?:\.\d+)?)\s+){8}-?(?:\d+(?:\.\d+)?)\s+[^\s]+\.dat$',re.I)
    record('EVAL-002', len(part_lines)==3 and all(pat.match(x) for x in part_lines), f'{len(part_lines)} type-1 lines checked')

    # EVAL-003 Swedish explicit requirements preserved.
    r=interpret('Bygg en liten röd traktor, ungefär 20 studs lång och max 250 delar.',catalog)
    ok=r['max_parts']==250 and r['target_envelope_studs']['depth']==20 and any(c['name']=='Red' for c in r['preferred_colors'])
    record('EVAL-003',ok,'max_parts/color/depth retained')

    # EVAL-004 max-parts blocks.
    bm=load(ROOT/'tests/static-validation/max-parts.invalid.json'); br=validate_model(bm,schema,catalog,allow_fixture=True)
    record('EVAL-004',br['result']=='fail' and any(f['code']=='MV400' for f in br['findings']),'MV400 expected')

    # EVAL-005 vague prompt gets defaults, no blocking question.
    vr=interpret('Bygg en katt.',catalog)
    record('EVAL-005',vr['detail_level']=='balanced' and vr['target_envelope_studs']['source']=='inferred' and not any(q['blocking'] for q in vr['open_questions']), 'conservative defaults')

    # EVAL-006 unknown part with no candidate abstains.
    resolution=resolve_failure(rep,catalog,[])
    record('EVAL-006',resolution['delivery_allowed'] is False and resolution['actions'][-1]['action']=='report_unverifiable','fail-closed abstention')

    # EVAL-007 invented candidate neither selected nor echoed.
    invented='987654321.dat'; resolution2=resolve_failure(rep,catalog,[invented])
    serialized=json.dumps(resolution2)
    record('EVAL-007',invented not in serialized and not resolution2['delivery_allowed'],'invented candidate discarded')

    # EVAL-008 English requirements preserved.
    er=interpret('Make a detailed blue display car, 24 studs long, at most 300 pieces.',catalog)
    ok=er['model_usage']=='display' and er['detail_level']=='detailed' and er['max_parts']==300 and er['target_envelope_studs']['depth']==24 and any(c['name']=='Blue' for c in er['preferred_colors'])
    record('EVAL-008',ok,'English requirements retained')

    summary={
      'schema_version':'1.0',
      'result':'pass' if all(r['result']=='pass' for r in results if r['required']) else 'fail',
      'statistics':{'total':len(results),'passed':sum(r['result']=='pass' for r in results),'failed':sum(r['result']=='fail' for r in results)},
      'categories':{}, 'results':results
    }
    for r in results:
        summary['categories'].setdefault(r['category'],{'passed':0,'failed':0})[r['result']=='pass' and 'passed' or 'failed']+=1
    (ROOT/'evals/results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in results: print(f"{r['result'].upper():4} {r['id']} {r['category']}: {r['description']}")
    print(f"Eval result: {summary['result'].upper()} ({summary['statistics']['passed']}/{summary['statistics']['total']} passed)")
    return 0 if summary['result']=='pass' else 1

if __name__=='__main__': raise SystemExit(main())
