# LDraw-export

Den interna JSON-modellen serialiseras deterministiskt av `scripts/ldraw_export.py`.

## Format

- En modell med exakt en submodell och utan submodellinstanser exporteras som `.ldr`.
- Flera submodeller exporteras som `.mpd` med `0 FILE <id>.ldr` / `0 NOFILE`.
- Fysiska delar och submodellinstanser serialiseras som LDraw type-1-rader.
- Position skrivs som X/Y/Z i LDU och rotation som nio värden i LDraws 3×3-matrisordning.
- Submodellinstanser använder färg 16 (current color) som standard.

## Determinism

Tal normaliseras utan onödiga decimaler och submodeller/delar behåller den explicita ordningen i canonical JSON. Samma input ger byte-identisk output.

## Ansvarsfördelning

Exportören verifierar serialisering och submodellreferenser, men ersätter inte katalogvalidering eller den statiska/geometriska validering som införs i kommande steg. En exporterad fil är därför inte automatiskt en verifierad LEGO-konstruktion.
