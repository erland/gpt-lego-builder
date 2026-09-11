# BrickLink Studio compatibility suite

Detta är projektets manuellt öppningsbara LDraw-testsvit.

| Fall | Fil | Syfte |
|---|---|---|
| 01 | `01-simple-ldr/model.ldr` | Enkel LDR |
| 02 | `02-multicolor-ldr/model.ldr` | Flera färger |
| 03 | `03-submodels-mpd/model.mpd` | MPD + submodeller |
| 04 | `04-rotation-ldr/model.ldr` | Ortogonal rotation |
| 05 | `05-larger-ldr/model.ldr` | 60 delar |

Kör `python scripts/test_studio_compatibility.py` för automatiska kontroller. Resultatet skrivs till `automated-results.json`.

Automatisk PASS betyder **inte** att BrickLink Studio har startats. GUI-import dokumenteras separat i `manual-studio-results.md`.
