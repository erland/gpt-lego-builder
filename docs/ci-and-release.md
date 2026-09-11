# CI och releasebygge

## CI

`.github/workflows/ci.yml` kör lint, schema-/unit-/integrationstester, evals, checkpoint-hygiene, ett rent distributionsbygge, distributionsvalidering, runtime parity, releaseartefaktverifiering och workflow-kontraktstest. Resultatet laddas även upp som GitHub Actions-artifact.

CI använder projektets lilla fixture-katalog. Den är avsedd för reproducerbara regressionstester, inte för produktionsverifiering av godtyckliga LEGO-delar.

## Release / testrelease

`.github/workflows/release.yml` kan startas på två sätt:

- automatiskt när en GitHub Release publiceras; GitHub Release-taggen är då auktoritativ version,
- manuellt via `workflow_dispatch` med ett explicit versionsnummer för ett testrelease-bygge utan publicering till en GitHub Release.

Ett inledande `v` tas bort, så taggen `v1.0.0` ger artefaktversion `1.0.0`.

Releasebygget hämtar LDraw `complete.zip`, bygger om katalogindexet som `official_release`, kör hela test-/evalkedjan mot den katalogen, kör final hygiene, bygger samtliga distributioner och verifierar checksummor samt leveransmanifest.

## Artefakter

Ett bygge för version `X` producerar:

- `lego-modellbyggaren-project-X.zip`
- `lego-modellbyggaren-chat-X.zip`
- `lego-modellbyggaren-custom-gpt-X.zip`
- `SHA256SUMS.txt`
- `DELIVERY-MANIFEST.json`

`dist/` rensas före varje bygge. Därmed kan en äldre ZIP inte följa med av misstag. `verify_release_artifacts.py` kräver exakt de tre ZIP-filerna för den aktuella versionen och verifierar både SHA-256-filen och leveransmanifestet.

## Kvarvarande manuell kontroll

Automatiken kan verifiera LDraw-formatet men inte starta BrickLink Studio. Den manuella Studio-checklistan från steg 9 kvarstår därför som releaseinformation tills den har körts i en faktisk Studio-installation.
