# Chat-runtime

Chat ZIP är avsedd att vara en portabel runtime-distribution för LEGO Modellbyggaren.
Den innehåller canonical instruktion, runtime-scheman, nödvändiga Python-script,
delkatalogens metadata/index samt dokumentation som instruktionen hänvisar till.

## Kritisk katalogregel

En slutmodell får endast markeras katalogverifierad när `catalog/catalog.json` har
`source.kind = official_release`.

Utvecklingsbyggen kan innehålla en liten `fixture`-katalog för självtest. Den får
aldrig användas som bevis för att en användarmodell är verifierad.

För en produktionskörning ska ett aktuellt officiellt LDraw `complete.zip` användas
för att bygga katalogen med `scripts/build_ldraw_catalog.py`. Källans URL och
versionspolicy finns i `catalog/source.yaml`.

## Runtimeflöde

1. Läs `START-HERE.md` och `assistant/instructions.md`.
2. Normalisera användarkrav med reglerna i instruktionen och vid behov
   `scripts/interpret_requirements.py`.
3. Skapa konstruktionsplan och intern modell enligt schemana.
4. Kontrollera att katalogen är `official_release` för en verklig leverans.
5. Kör `scripts/validate_model.py` eller `scripts/export_validated_model.py`.
6. Leverera endast `.ldr/.mpd` om leveransgaten passerar.
7. Vid fel: följ fallbackordningen i `docs/failure-handling.md`.

## Självtest

Kör:

```bash
python scripts/runtime_self_test.py
```

Självtestet använder den medföljande fixture-katalogen och verifierar endast att
runtime-paketets beroenden och kärnkomponenter fungerar tillsammans. Det är inte
en produktionsverifiering av en LEGO-modell.
