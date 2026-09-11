# Scripts

Projekt-, schema-, katalog-, validerings-, distributions- och LDraw-exportverktyg finns här.

Viktiga kommandon:

- `validate_model_schema.py` – ren JSON Schema-validering.
- `build_ldraw_catalog.py` – bygger verifierat part- och färgindex från LDraw-biblioteket och `LDConfig.ldr`.
- `validate_model_catalog.py` – enkel fail-closed kontroll av delreferenser mot LDraw-katalogen.
- `validate_model.py` – full blockerande statisk validering med maskinläsbar rapport.
- `ldraw_export.py` – låg-nivå, deterministisk serialisering till `.ldr`/`.mpd`; ska inte ensam användas som leveransgate.
- `export_validated_model.py` – rekommenderad säker runtime-export: validera först, exportera endast vid PASS.
- `test_static_model_validation.py` – regressionstest för schema, katalog, färg, rotationer, submodellgraf, delgräns och exportgate.

- `failure_handling.py` – skapar en fail-closed reparationsplan från valideringsfel; ersättningsdelar måste finnas i katalogen.
- `test_failure_handling.py` – regressionstest för verifierad ersättning, omkonstruktion, förenkling och explicit avstående utan påhittade del-ID:n.
