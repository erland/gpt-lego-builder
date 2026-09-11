#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import jsonschema
from ldraw_catalog import load_catalog
from model_validation import load_schema, validate_model
from ldraw_export import export_model


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    ap=argparse.ArgumentParser(description='Run the step-7 reference flow from text requirement artifacts to validated LDraw')
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--scenario', default='examples/end-to-end-red-tower')
    ap.add_argument('--catalog', default='catalog/catalog.json')
    ap.add_argument('--allow-fixture', action='store_true')
    args=ap.parse_args()

    root=Path(args.project_root).resolve()
    scenario=(root/args.scenario).resolve()
    prompt=(scenario/'prompt.txt').read_text(encoding='utf-8').strip()
    plan=load_json(scenario/'construction-plan.json')
    model=load_json(scenario/'model.json')

    if model['requirements']['source_prompt'] != prompt:
        raise SystemExit('End-to-end FAIL: model source_prompt differs from prompt.txt')

    plan_schema=load_json(root/'schemas/construction-plan.schema.json')
    jsonschema.Draft202012Validator(plan_schema).validate(plan)

    catalog=load_catalog(root/args.catalog)
    report=validate_model(model, load_schema(root), catalog, allow_fixture=args.allow_fixture)
    (scenario/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if report['result'] != 'pass':
        raise SystemExit('End-to-end FAIL: static validation failed; see validation-report.json')

    out=scenario/'red-tower.ldr'
    export_model(model,out,'ldr')
    print(f'End-to-end reference: PASS ({prompt!r} -> {out.relative_to(root)})')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
