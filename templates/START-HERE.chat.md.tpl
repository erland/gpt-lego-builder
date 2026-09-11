# {{GPT_NAME}} – Chat ZIP

Detta är den portabla Chat-runtime-distributionen för **{{GPT_NAME}}**.

## Start

1. Läs detta dokument.
2. Läs därefter `assistant/instructions.md` och följ den som GPT:ns canonical runtimeinstruktion.
3. Använd endast de runtimefiler som finns i ZIP:en; utvecklingsprojektet ska inte behövas.
4. Läs `RUNTIME.md` för körflöde och katalogregler.

## Kritisk verifieringsregel

En slutlig användarmodell får endast kallas katalogverifierad när
`catalog/catalog.json` anger `source.kind = official_release`.

Om den medföljande katalogen är `fixture` är den bara avsedd för utvecklings- och
självtest. Ska en riktig modell levereras måste en aktuell officiell LDraw-katalog
byggas först enligt `RUNTIME.md` och `catalog/source.yaml`. Om det inte går ska
runtime falla stängt och inte hitta på delar.

## Runtimeinnehåll

- `assistant/instructions.md` – canonical runtimeinstruktion
- `assistant/policies/` – runtimepolicies
- `knowledge/` – kompletterande referensmaterial
- `docs/` – dokument som canonical instruktion hänvisar till
- `schemas/` – interna runtime-scheman
- `scripts/` – endast de script som behövs för kärnflödet
- `catalog/` – delkatalog/index och källmetadata
- `RUNTIME.md` – portabilitets- och körinstruktion
- `MANIFEST.json` – maskinläsbar fil- och checksummeförteckning

## Självtest

Om Python-runtime finns tillgänglig kan paketet verifieras med:

```bash
python scripts/runtime_self_test.py
```

Självtestet använder fixture-katalog och är inte ett bevis på produktionsverifiering.

## Version

{{VERSION}}
