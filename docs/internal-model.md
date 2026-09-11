# Intern modellrepresentation

## Syfte

Den interna modellen är en deterministiskt validerbar brygga mellan fri text och LDraw. Språkmodellen ska inte behöva komponera den slutliga `.ldr`/`.mpd`-filen direkt.

## Flöde

```text
textkrav
  ↓
kravtolkning
  ↓
intern modell (JSON)
  ↓
schema-validering
  ↓
katalogvalidering (steg 3)
  ↓
geometrisk kontroll (senare steg)
  ↓
LDraw-serialisering (steg 4)
```

## Toppnivå

| Fält | Betydelse |
|---|---|
| `schema_version` | Version på mellanformatet. |
| `metadata` | Modell-ID, namn, beskrivning och livscykelstatus. |
| `requirements` | Ursprunglig prompt och härledda konstruktionskrav. |
| `dimensions` | Modellens uppskattade bounding box i LDU. |
| `submodels` | Delmodeller och placerade delar. |
| `validation` | Samlad status för schema-, katalog- och geometrikontroll. |

## Delrepresentation

Varje placerad del innehåller:

- ett lokalt unikt `instance_id`,
- `ldraw_part`, som är ett LDraw-del-filnamn,
- numerisk LDraw-färgkod,
- position `(x, y, z)` i LDU,
- en 3×3 rotationsmatris,
- separat valideringsstatus för katalogreferens och placering.

## Mapping till LDraw

En LDraw type-1-rad har principiellt formen:

```text
1 <colour> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <file>
```

Mappingen från intern modell blir:

| LDraw | Intern modell |
|---|---|
| `colour` | `part.color` |
| `x y z` | `part.placement.position.x/y/z` |
| `a..i` | `part.placement.rotation[0..8]` |
| `file` | `part.ldraw_part` |

Exportören i steg 4 får endast serialisera delar som har passerat de valideringar som då är tillgängliga.

## Valideringsnivåer

### Schema

Kontrollerar bland annat obligatoriska fält, datatyper, rotationsmatrisens längd och formen på LDraw-filnamnet.

### Katalog

Kontrollerar att `ldraw_part` faktiskt finns i den auktoritativa katalogen. **Inte implementerat i steg 2.**

### Geometri

Kontrollerar senare grundläggande placering och kollisioner. **Inte implementerat i steg 2.**

## Viktig säkerhetsregel

`*.valid.json` betyder endast *schema-valid*. En modell får inte presenteras som fullständigt verifierad förrän katalog- och tillämplig geometrivalidering också har passerat.

## Katalogverifiering (steg 3)

Fältet `part.validation.catalog_reference` är en rapporterad status, inte ett bevis i sig. Beviset kommer från en lyckad kontroll av `ldraw_part` mot `catalog/catalog.json` där katalogens `source.kind` måste vara `official_release` i produktionsflödet.

Utvecklings-fixtures får endast användas i tester. Okänd delreferens eller otillgänglig katalog är ett blockerande katalogfel.
