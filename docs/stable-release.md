# Stabil release 1.0

Stabil `1.0.0` får endast byggas när alla automatiska quality gates passerar **och** den manuella BrickLink Studio-verifieringen är genomförd.

`python scripts/verify_stable_release.py --project-root . --version 1.0.0` blockerar stabil release om `examples/studio-compatibility/manual-studio-results.md` inte har `**Status:** pass` eller fortfarande innehåller `ej testad`.

Prerelease-versioner som `1.0.0-rc.2` får byggas även när GUI-verifieringen återstår.

## Praktiskt slutsteg

1. Öppna samtliga golden `.ldr/.mpd`-filer i BrickLink Studio.
2. Kontrollera delantal, färger, orientering, submodeller och att filen kan sparas som `.io`.
3. Fyll i `manual-studio-results.md` och sätt `**Status:** pass` om samtliga fall är godkända.
4. Kör stable gate och hela releasekedjan för `1.0.0`.
