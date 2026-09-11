# Schemas

## `model.schema.json`

Canonical JSON Schema för LEGO Modellbyggarens interna mellanrepresentation.

Representationen ligger mellan användarens textkrav och LDraw-exporten. GPT:n ska därför skapa eller uppdatera en modell enligt detta schema innan export.

### Viktiga designval

- `schema_version` är låst till `1.0`.
- Positioner anges i **LDraw Units (LDU)**.
- Rotation anges som nio tal i samma 3×3-matrisordning som senare kan mappas till en LDraw type-1-rad.
- `ldraw_part` måste ha formen av ett LDraw `.dat`-filnamn.
- Schemat kan upptäcka en **malformerad** delreferens men kan inte avgöra om filnamnet faktiskt finns i LDraw-biblioteket. Den katalogkontrollen införs i steg 3.
- Delens katalogstatus börjar normalt som `unverified`.
- Modellens `validation.catalog` och `validation.geometry` ska förbli `pending` tills respektive validator faktiskt har körts.

### Exempel

`schemas/examples/simple-table.valid.json` är ett strukturellt giltigt exempel. Namnet på filen innebär bara att JSON-strukturen är giltig; det innebär inte att modellen redan är katalog- eller geometriverifierad.
