# Stud.io-kompatibilitet – verifieringsstrategi

## Syfte

Målmiljön är BrickLink Studio. Studio stöder att öppna eller importera LDraw-modeller i `.ldr`- och `.mpd`-format. Projektet använder därför standard-LDraw som integrationskontrakt och håller GUI-verifiering separat från maskinell filvalidering.

## Vad vi verifierar automatiskt

Kompatibilitetssviten i `examples/studio-compatibility/` omfattar fem representativa fall:

1. enkel `.ldr` med en verifierad del,
2. `.ldr` med flera LDraw-färger,
3. `.mpd` med huvudmodell och återanvänd submodell,
4. `.ldr` med ortogonal 90-gradersrotation,
5. större `.ldr` med 60 delar.

`python scripts/test_studio_compatibility.py` kräver att varje fall:

- passerar modellens schema-, katalog-, struktur- och blockerande geometrikontroller,
- får förväntat expanderat antal delar,
- exporteras till förväntat LDraw-format,
- endast innehåller syntaktiskt välformade type-1-rader för placeringar,
- använder korrekt `0 FILE`/`0 NOFILE`-struktur i MPD-fallet,
- producerar en deterministisk golden-fil som kan öppnas manuellt i Studio.

## Vad vi inte påstår automatiskt

Testsviten startar inte BrickLink Studio och påstår därför inte att GUI-import faktiskt har genomförts. En LDraw-fil som följer standarden och använder katalogdelar är en stark förutsättning för Studio-kompatibilitet, men Studio kan ha egen delmappning eller beteenden som bara kan observeras i programmet.

Den manuella verifieringen är därför en separat release-check och ska aldrig ersättas av texten `automated-results.json`.

## Manuell Studio-checklista

För varje fil i kompatibilitetssviten:

1. öppna filen i BrickLink Studio,
2. kontrollera att inga okända/dummy-delar visas,
3. kontrollera att delantalet motsvarar `expected_expanded_parts`,
4. kontrollera färger visuellt,
5. kontrollera position/orientering visuellt,
6. för MPD: kontrollera att submodellen finns och att båda instanserna visas,
7. spara modellen som `.io` utan att först behöva reparera LDraw-syntax.

Resultatet kan dokumenteras i `manual-studio-results.md`. Fram till dess ska status vara `not_run`.

## Kända begränsningar

- Testkatalogen är en utvecklingsfixture med endast ett litet antal verkliga LDraw-delar.
- Historisk tillgänglighet för del + färg verifieras ännu inte.
- Geometri v1 bevisar inte connection, stabilitet eller full kollisionsfrihet.
- Roterade basdelar får `geometry: partial` eftersom deras kollisions-envelope ännu inte beräknas.
