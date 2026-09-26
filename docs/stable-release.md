# Stabil release 1.0

Stabil **1.0.0** får endast publiceras när både de automatiska quality gates i release-workflowet och den manuella BrickLink Studio GUI-verifieringen är godkända.

Den manuella verifieringen är en **blockerande stable-release-gate**. Den får inte tolkas som godkänd förrän `examples/studio-compatibility/manual-studio-results.md` uttryckligen har status `pass`.

## Obligatorisk Studio-kontroll

1. Öppna samtliga golden `.ldr/.mpd`-filer i BrickLink Studio.
2. Kontrollera delantal, färger, orientering, submodeller och att filen kan sparas som `.io`.
3. Fyll i `examples/studio-compatibility/manual-studio-results.md`.
4. Sätt status till `pass` endast efter faktisk genomförd kontroll.

## Automatiska gates

Release-workflowet kräver fortsatt lint, tester, evals, hygiene, distributionsvalidering, runtime parity, official LDraw release-katalog och verifiering av releaseartefakter.

## Aktuell status

Version **1.0.0-rc.2** är RC-klar. Den manuella BrickLink Studio-verifieringen står på `not_run`, därför är stabil **1.0.0** fortsatt blockerad.
