# Stabil release 1.0

En stabil release byggs när de automatiska quality gates i release-workflowet passerar.

Den manuella BrickLink Studio-verifieringen är rekommenderad som extra kontroll, men den blockerar inte längre en stabil release.

## Rekommenderad Studio-kontroll

1. Öppna samtliga golden `.ldr/.mpd`-filer i BrickLink Studio.
2. Kontrollera delantal, färger, orientering, submodeller och att filen kan sparas som `.io`.
3. Fyll vid behov i `examples/studio-compatibility/manual-studio-results.md` för dokumentation.

Release-workflowet fortsätter att kräva övriga automatiska kontroller: lint, tester, evals, hygiene, distributionsvalidering, runtime parity och verifiering av releaseartefakter.
