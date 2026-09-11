# Konstruktionsstrategi – runtime-sammanfattning

Följ alltid denna ordning när en textbeskrivning ska bli en LEGO-modell:

1. Tolka motiv, funktion/display, storlek, färger, detaljnivå, maxdelar och uttryckliga begränsningar.
2. Härled konservativa standarder när ofarliga detaljer saknas; fråga bara om ett verkligt designval är avgörande.
3. Bestäm ungefärligt envelope i studs och välj `simple`, `balanced` eller `detailed`.
4. Dela motivet i 2–7 huvudsektioner och bygg bärande struktur före detaljer.
5. Version 1 prioriterar studs-up, bricks, plates och enkla ortogonala rotationer. Undvik fria vinklar, flex, komplex Technic och connection-känslig SNOT när det inte kan verifieras.
6. Välj delar endast från katalogen. Föredra återanvändning och en liten uppsättning enkla deltyper.
7. Skapa först en plan enligt `schemas/construction-plan.schema.json`, därefter modellen enligt `schemas/model.schema.json`.
8. Kör blockerande statisk validering och exportera endast genom den säkra exportvägen.
9. Vid fel: byt till annan verifierad del → ändra dimension/lager → förenkla sektion → ta bort icke-kritisk detalj → minska detaljnivå → rapportera att kravet inte kan verifieras.
10. Påstå aldrig att fysisk stabilitet, connections eller full kollisionsfrihet är verifierade innan särskilda kontroller finns.
