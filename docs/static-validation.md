# Statisk modellvalidering

Steg 5 inför en blockerande valideringspipeline mellan intern JSON-modell och levererbar LDraw-fil.

## Säker exportväg

Använd i runtime:

```bash
python scripts/export_validated_model.py model.json catalog/catalog.json output.mpd
```

För utvecklingstester får en fixture användas explicit med `--allow-fixture`. En fixture får aldrig användas som produktionsbevis.

## Kontroller

Validatorn kontrollerar:

- JSON Schema för hela mellanmodellen,
- att katalogen är `official_release` i produktionsläge,
- att varje `ldraw_part` finns och är godkänd som modellpart,
- att del- och submodellfärger finns i katalogens index av `LDConfig.ldr`,
- att positioner består av ändliga numeriska värden,
- att rotationer är ortonormala 3×3-matriser med determinant +1,
- unika submodell-ID:n och globala `instance_id`,
- existerande submodellreferenser,
- inga själv- eller indirekta cykler,
- att alla submodeller nås från den första/root-submodellen,
- utökat fysiskt delantal genom submodellinstanser mot `requirements.max_parts`,
- rimlig ordning på modellens deklarerade min/max-gränser.

Validatorn producerar en maskinläsbar rapport med resultat, delkontroller, statistik och stabila felkoder.

## Avgränsning

`checks.geometry` kompletteras från steg 8 av den konservativa geometri-validatorn. `passed` betyder bara att de implementerade v1-reglerna passerat och `partial` att någon del inte kunde profileras. Valideringen bevisar inte:

- kollisionsfrihet,
- korrekta stud/anti-stud-kopplingar,
- hållfasthet eller stabilitet,
- fysisk byggbarhet,
- historisk tillgänglighet av en viss del/färg-kombination.

Dessa egenskaper får därför inte påstås vara verifierade av steg 5.
