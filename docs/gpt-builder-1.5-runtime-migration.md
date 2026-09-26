# GPT Byggaren 1.5.0 – migreringsplan

Projekt: **LEGO Modellbyggaren**

Utgångsläge:
- produktplan **18/18 complete**
- version **1.0.0-rc.2**
- Chat ZIP och Custom GPT implementerade
- stable-release är enligt aktuell projektstatus blockerad tills manuell BrickLink Stud.io-verifiering har status `pass`
- `examples/studio-compatibility/manual-studio-results.md` står på `not_run`

## Mål

Migrera LEGO Modellbyggaren till GPT Byggaren 1.5.0 utan att förändra produktbeteendet, de fail-closed säkerhetsreglerna, versionsstatusen eller releasebeslutet.

## Preserve-first

Följande ska bevaras:

- `assistant/instructions.md` som canonical beteendekontrakt.
- `gpt-project.yaml` som central projektkonfiguration.
- `VERSION` = `1.0.0-rc.2` tills en separat versionsändring görs.
- Produktplan **18/18 complete**.
- `VERIFIERADE DELAR ENDAST`.
- `STUDIO-KOMPATIBEL EXPORT`.
- `INGEN FALSK FYSIKGARANTI`.
- Fail-closed validerings- och exportkedja.
- Official LDraw-katalog som krav för produktionsverifiering.
- Chat ZIP och Custom GPT som befintliga runtimes.
- Custom GPT som behavior-parity med reducerad execution-parity.
- Befintliga tester, evals, parity- och releasegates.
- Manuell BrickLink Stud.io-status `not_run` tills faktisk extern verifiering har gjorts.

## Stable-release policy under migration

Migreringen får inte ändra den manuella Stud.io-verifieringen till `pass`, och får inte automatiskt avblockera stabil `1.0.0`.

Det finns i nuläget en dokumentationskonflikt:
- `project-status.yaml`, `STATUS.md` och `docs/release-readiness.md` behandlar GUI-verifieringen som blockerande.
- `docs/stable-release.md` säger att GUI-verifieringen inte längre blockerar.

Under migreringen gäller preserve-first: den konservativa blockerande tolkningen behålls tills konflikten explicit löses i steg 9. Ingen produktpolicyändring ska smygas in genom migreringen.

## Runtime-målbild

Aktiva runtimes efter migrering:

1. ChatGPT Chat
2. ChatGPT Custom GPT
3. Claude Projects
4. OpenCode

Avsedd 1.5 compatibility:

- Chat: `equivalent_runtime_dependent`
- Custom GPT: `equivalent_with_platform_constraints`
- Claude Projects: `reduced`
- OpenCode: `equivalent`

OpenAI Plugin ska bedömas men inte automatiskt aktiveras. Preliminär målbild: `not_active / reduced / advisory_only`.

## Steg

### 1. Separat 1.5-migrationsstatus
Inför separat migrationsplan/status och lås preserve-first-reglerna.

### 2. Normalisera canonical kontrakt
Inför explicit capability-, artifact-, workspace/state- och tool-kontrakt för 1.5 utan att ändra LEGO-reglerna.

### 3. Runtime/distribution registry
Gör runtime-set, artifactnamn, compatibility och release-assets deklarativa.

### 4. Verifiera Chat
Verifiera canonical instruktion, katalog/schemas, deterministiska validatorer och fail-closed export.

### 5. Verifiera Custom GPT
Verifiera instruktion/Knowledge, katalogreferens, Code Interpreter-beroenden och no-false-PASS.

### 6. Inför Claude Projects och OpenCode
Generera och verifiera Claude reduced samt OpenCode equivalent utan att försvaga katalog-/valideringsregler.

### 7. OpenAI Plugin compatibility assessment
Lås plugin som advisory only om full fil/state/validation/artifact parity inte kan bevisas.

### 8. Generalisera build, parity, CI och release
Härled aktiva runtimes och exakt artifact-set från registryt. Bevara official LDraw release-catalog-steget och stable-release-gaten.

### 9. Slutlig readiness och dokumentationssynk
Synka README/STATUS/migrationsstatus, lägg final 9/9-gate och lös den interna stable-release-dokumentationskonflikten utan att ändra manuell `not_run` till `pass`.
