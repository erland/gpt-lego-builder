# LDraw-katalog

`catalog.json` är ett kompakt index av godkända top-level LDraw-parts och definierade LDraw-färger.

- Parts indexeras från `parts/*.dat` med godkänd `!LDRAW_ORG`-typ.
- Subparts/primitives används inte som direkt valbara modellparts.
- Färgkoder indexeras från `LDConfig.ldr`.
- `source.kind=fixture` är endast utveckling/test.
- En slutmodell får endast kallas katalogverifierad mot `source.kind=official_release`.
- Katalogvalidering bevisar inte historisk part/färg-tillgänglighet.
