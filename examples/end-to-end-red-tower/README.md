# Första end-to-end-modellen

Detta scenario bevisar den tekniska kedjan från ett textkrav till en validerad LDraw-fil.

## Textkrav

> Bygg ett litet rött torn av tre vanliga 2 x 4-klossar staplade rakt ovanpå varandra.

## Artefakter

- `prompt.txt` – ursprungligt textkrav.
- `construction-plan.json` – schema-validerad konstruktionsplan.
- `model.json` – intern modellrepresentation.
- `validation-report.json` – rapport från den blockerande statiska valideringen.
- `red-tower.ldr` – exporterad LDraw-modell.

## Avgränsning

Utvecklingsmiljön använder en liten katalog-fixture för regressionstest. Därför körs scenariot med `allow_fixture=True` och får inte användas som bevis för produktionskatalog. Samma exportgate kräver `official_release` utan detta testundantag.

BrickLink Studio stöder import/öppning av `.ldr` och `.mpd`. Praktisk GUI-verifiering i Studio görs systematiskt i steg 9; steg 7 verifierar formatkedjan och producerar en standard-LDraw-fil utan manuell syntaxbearbetning.
