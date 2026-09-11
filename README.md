# LEGO Modellbyggaren

Ett GPT-projekt för att skapa verifierade LDraw-kompatibla LEGO-modeller från textbeskrivningar och öppna dem i BrickLink Stud.io.

## Status

Steg 8 av 18 är genomfört. Projektet har nu hela kedjan från textkrav till verifierad LDraw-export samt konservativ geometrivalidering för enkla Brick/Plate-delar. Nästa steg är systematisk Stud.io-kompatibilitet.

## Viktiga filer

- `assistant/instructions.md` – canonical GPT-instruktion
- `gpt-project.yaml` – projektkonfiguration
- `project-status.yaml` – maskinläsbar status
- `docs/development-plan.md` – stegvis utvecklingsplan
- `docs/static-validation.md` – blockerande valideringsregler
- `docs/geometry-validation.md` – geometriska v1-regler
- `schemas/model.schema.json` – intern modellrepresentation
- `catalog/catalog.json` – verifierat del- och färgindex
- `scripts/validate_model.py` – statisk validator och JSON-rapport
- `scripts/export_validated_model.py` – säker exportväg

## Säkerhetsprincip för export

En slutfil ska exporteras genom `export_validated_model.py`. Den vägen skapar ingen `.ldr`/`.mpd` om schema-, katalog-, struktur- eller blockerande geometrikontroller fallerar.

## Distributioner

Projektet är strukturerat för både Chat ZIP och Custom GPT. Funktionell runtime-paritet valideras i senare steg.

## Del- och färgkatalog

Delidentiteter och LDraw-färgkoder verifieras mot ett kompakt index byggt från LDraw.org Official Parts Library inklusive `LDConfig.ldr`. Utvecklingsprojektet innehåller en minimal fixture; GitHub Release-flödet bygger den fulla `official_release`-katalogen från LDraws `complete.zip` innan Chat- och Custom GPT-paketen skapas.

## Konstruktionsstrategi

Textkrav struktureras först i `schemas/construction-plan.schema.json` enligt `docs/construction-strategy.md`. Planen är ett arbetsunderlag; den interna modellen och den blockerande validatorn är fortfarande leveransgaten.

## Första end-to-end-referensen

Steg 7 innehåller scenariot `examples/end-to-end-red-tower/`. Kör:

```bash
python scripts/run_reference_end_to_end.py --project-root . --allow-fixture
```

Det verifierar planformat, modell, katalogreferenser och statisk gate och producerar `red-tower.ldr`. `--allow-fixture` är enbart för regressionstest; slutliga modeller kräver en `official_release`-katalog.

## Kravtolkning

Fri text normaliseras enligt `docs/requirement-interpretation.md` och `schemas/interpreted-request.schema.json`. `scripts/interpret_requirements.py` ger ett deterministiskt v1-resultat med uttryckliga krav, härledda antaganden och eventuella blockerande öppna frågor.

## Säker felhantering

Steg 11 inför en fail-closed reparationsplan. Okända delreferenser får aldrig ersättas med gissade ID:n; endast exakta katalogträffar får användas som `replacement_part`. Se `docs/failure-handling.md`.

## Evals

`python scripts/run_evals.py` kör den blockerande produkt-evalsviten. Se `docs/evals.md` och `evals/cases.json`.

## Custom GPT-runtime

Från 0.14.0-dev byggs Custom GPT som en separat runtime-distribution med kompilerad instruktion, explicit capability-konfiguration, schemas/katalog/referensdokument som Knowledge, Preview-checklista och en dokumenterad parity-bedömning. Code Interpreter & Data Analysis krävs för full `.ldr/.mpd`-filgenerering. Custom GPT har samma beteendekontrakt men reducerad execution-parity jämfört med Chat ZIP eftersom samma lokala Python-script inte kan garanteras som obligatorisk gate i varje GPT-konversation.

## Runtime parity

Chat ZIP och Custom GPT byggs från samma canonical beteendekontrakt. Chat-versionen har full deterministisk scriptbaserad validering, medan Custom GPT i version 1 har reducerad execution parity. `scripts/test_runtime_parity.py` verifierar kritiska regler, obligatoriska referenser, versionsintegritet och runtime-hygiene. Se `docs/runtime-parity-and-hygiene.md`.


## CI och release

CI och releasebygge beskrivs i `docs/ci-and-release.md`. Releaseflödet kan även köras manuellt som testrelease och producerar versionsmärkta projekt-, Chat- och Custom GPT-ZIP:ar med SHA-256-checksummor och leveransmanifest.
