# Utvecklingsplan – LEGO-modellbyggare för Stud.io

## Projektmål

Bygg en GPT som tar emot en textuell beskrivning av ett LEGO-bygge och producerar en digital modellfil som kan öppnas i BrickLink Stud.io.

GPT:n ska prioritera korrekthet framför kreativ frihet:

- endast verifierade, verkliga LEGO/LDraw-delar får användas,
- inga påhittade artikelnummer eller delreferenser får förekomma,
- modellen ska använda giltig LDraw-syntax,
- användaren ska kunna öppna resultatet i Stud.io och därifrån själv skapa bygginstruktioner.

## Rekommenderad projektprofil

`zip_first_advanced`

Skälet är att lösningen behöver:

- canonical GPT-instruktion,
- strukturerad mellanrepresentation av modellen,
- scripts för validering och export,
- tester/evals,
- katalogdata eller katalogindex för verifiering,
- Chat ZIP och Custom GPT som separata distributioner från samma beteendekontrakt.

## Version 1 – avgränsning

Version 1 ska kunna:

1. ta emot en fri textbeskrivning,
2. härleda rimliga byggbegränsningar,
3. planera modellen som delmodeller/sektioner,
4. välja delar endast ur verifierad katalog,
5. placera delar i LDraw-koordinater med rotation,
6. validera delreferenser och syntax,
7. exportera `.ldr` eller `.mpd`,
8. leverera modellfilen till användaren,
9. rapportera osäkerheter i stället för att hitta på delar.

Version 1 behöver inte:

- generera en färdig PDF-byggmanual,
- bevisa full mekanisk hållfasthet,
- optimera mot global lägsta kostnad,
- garantera att varje del/färg-kombination historiskt har sålts av LEGO,
- simulera fysik.

---

# Stegvis utvecklingsplan

## Steg 1 – Skapa projektgrund och canonical kontrakt

### Mål

Skapa projektstrukturen och definiera GPT:ns kärnbeteende.

### Leverans

- `gpt-project.yaml`
- `PROJECT.md`
- `README.md`
- `STATUS.md`
- `project-status.yaml`
- `docs/development-plan.md`
- canonical instruktion
- grundläggande capability-kontrakt
- initial Chat/Custom-GPT-struktur

### Centrala regler

Canonical instruktionen ska bland annat slå fast:

- aldrig hitta på en LEGO-del,
- aldrig hitta på ett LDraw-filnamn,
- använd endast katalogverifierade delreferenser,
- valideringsfel ska leda till omkonstruktion eller tydlig varning,
- Stud.io är målmiljön för fortsatt visuell granskning och instruktionstillverkning.

### Klart när

- projektet går att bygga som projekt-ZIP,
- grundläggande lint passerar,
- status och plan är synkroniserade.

---

## Steg 2 – Definiera intern modellrepresentation

### Mål

Skapa ett strukturerat mellanformat så att GPT:n inte behöver skriva LDraw direkt från fri text.

### Föreslagen struktur

Modellen bör minst kunna representera:

- metadata,
- användarkrav,
- modellens uppskattade dimensioner,
- delmodeller,
- delar,
- LDraw-del-ID,
- färg-ID,
- position X/Y/Z,
- rotationsmatris,
- valideringsstatus.

### Leverans

- JSON Schema för intern modellrepresentation,
- exempelmodell,
- dokumenterad mapping till LDraw.

### Klart när

- giltiga exempel passerar schema-validering,
- ogiltiga part-referenser och ofullständiga placeringar kan upptäckas.

---

## Steg 3 – Bygg verifierad delkatalog

### Mål

Skapa den auktoritativa katalog som GPT:n får välja delar från.

### Princip

LDraw-biblioteket används som primär sanningskälla för exportens delreferenser.

Katalogen bör åtminstone innehålla:

- LDraw-filnamn,
- delnamn,
- delkategori,
- eventuellt LEGO Design ID när det går att mappa säkert.

### Leverans

- katalogbyggarscript,
- kompakt katalog/index som lämpar sig för runtime,
- dokumentation av källa och versionshantering.

### Klart när

- en refererad del kan verifieras deterministiskt,
- okända delar avvisas,
- GPT:n aldrig behöver gissa filnamn.

---

## Steg 4 – Implementera LDraw-export

### Mål

Konvertera den interna modellen till syntaktiskt korrekt `.ldr` eller `.mpd`.

### Leverans

- exportscript,
- stöd för LDraw typ-1 part lines,
- färg,
- position,
- rotationsmatris,
- submodels för `.mpd`,
- deterministisk output.

### Klart när

- flera testmodeller exporteras,
- exporterad syntax valideras,
- filer går att öppna i en LDraw-kompatibel miljö.

---

## Steg 5 – Implementera statisk modellvalidering

### Mål

Stoppa fel innan användaren får modellfilen.

### Kontroller

Minst:

- varje del finns i katalogen,
- varje delrad har giltigt format,
- färg-ID är syntaktiskt giltigt,
- koordinater och rotationer är numeriskt giltiga,
- submodels refereras korrekt,
- inga uppenbara saknade referenser finns.

### Leverans

- validator,
- maskinläsbar valideringsrapport,
- tydliga felmeddelanden.

### Klart när

- avsiktligt felaktiga modeller blockeras,
- korrekta testmodeller passerar.

---

## Steg 6 – Lägg till konstruktionsstrategi

### Mål

Ge GPT:n en konsekvent metod för att omvandla text till LEGO-geometri.

### Arbetsgång

GPT:n ska:

1. tolka användarens mål,
2. uppskatta skala,
3. identifiera huvudvolymer,
4. dela upp modellen i sektioner,
5. välja enkla och robusta LEGO-tekniker,
6. prioritera vanliga delar,
7. bygga från bärande struktur till detaljer,
8. skapa intern modellrepresentation,
9. validera,
10. konstruera om vid fel.

### Klart när

GPT:n kan beskriva och strukturera flera enkla modelltyper på ett reproducerbart sätt.

---

## Steg 7 – Skapa första end-to-end-modellen

### Mål

Bevisa hela kedjan på ett enkelt bygge.

### Rekommenderat testobjekt

En liten enkel modell, exempelvis:

- pall,
- bord,
- enkel låda,
- liten stuga,
- enkel bil.

### Flöde

Textbeskrivning → intern modell → katalogvalidering → LDraw-export → slutlig modellfil.

### Klart när

- GPT:n kan generera filen från ett textkrav,
- alla delar verifieras,
- filen kan öppnas i Stud.io utan manuell syntaxreparation.

---

## Steg 8 – Lägg till geometriska grundregler

### Mål

Minska risken för delar som är giltiga var för sig men placerade på orimliga sätt.

### Första regeluppsättning

- stud-grid,
- brick/plate-höjder,
- grundläggande ortogonala rotationer,
- undvik uppenbara överlappningar,
- enkel kontroll av närliggande bounding boxes,
- konservativa byggtekniker i första versionen.

### Viktig avgränsning

Detta är inte en full fysikmotor.

### Klart när

vanliga uppenbara placeringsfel upptäcks automatiskt.

---

## Steg 9 – Testa Stud.io-kompatibilitet systematiskt

### Mål

Verifiera att exporter fungerar i den faktiska målmiljön.

### Testfall

Minst:

- enkel modell,
- modell med flera färger,
- modell med submodels,
- modell med rotation,
- modell med många delar.

### Leverans

- kompatibilitetsrapport,
- dokumenterade begränsningar,
- korrigeringar i exportformatet vid behov.

### Klart när

testfilerna öppnas korrekt i Stud.io.

---

## Steg 10 – Förbättra användardialog och kravtolkning

### Mål

Göra GPT:n användbar utan att användaren behöver förstå LDraw.

### Exempel på naturliga krav

- “ungefär 20 studs bred”
- “max 300 delar”
- “mest röd och svart”
- “en enkel modell för ett barn”
- “mer displaymodell än leksak”
- “håll den kompakt”

GPT:n ska härleda rimliga tekniska val där det går och endast fråga om verkliga designval som inte kan härledas.

### Klart när

flera olika formuleringar leder till konsekvent strukturerade modellkrav.

---

## Steg 11 – Hantera misslyckad konstruktion säkert

### Mål

Säkerställa att modellen aldrig löser problem genom hallucination.

### Regler

Vid problem ska GPT:n i denna ordning:

1. försöka välja annan verifierad del,
2. ändra konstruktionen,
3. förenkla detaljen,
4. förklara begränsningen.

Den får inte:

- skapa ett nytt partnummer,
- anta att en del existerar,
- märka en overifierad modell som färdig.

### Klart när

evals visar att GPT:n avstår eller konstruerar om i stället för att hitta på delar.

---

## Steg 12 – Evals och regressionstester

### Mål

Mäta de viktigaste kvalitetskraven.

### Eval-kategorier

- hallucinerade delar,
- ogiltiga LDraw-referenser,
- syntaxfel,
- användarkrav som tappas bort,
- för stora modeller,
- otillåtna förenklingar,
- robusthet vid vaga beskrivningar,
- korrekt avstående när konstruktionen inte kan verifieras.

### Klart när

kritiska testfall passerar och blockerande regressioner kan upptäckas automatiskt.

---

## Steg 13 – Chat ZIP-runtime

### Mål

Bygga en komplett portabel Chat-version.

### Leverans

- Chat ZIP,
- `START-HERE.md`,
- runtime-instruktioner,
- nödvändiga schemas/scripts/katalogdata,
- validerad manifeststruktur.

### Klart när

en ny konversation kan använda ZIP-filen och genomföra kärnflödet utan projektets utvecklingsfiler.

---

## Steg 14 – Custom GPT-distribution

### Mål

Bygga motsvarande Custom GPT från samma canonical kontrakt.

### Fokus

Identifiera vilka delar av kärnflödet som fungerar direkt och vilka som begränsas av Custom GPT-miljön.

### Leverans

- kompilerad Custom GPT-instruktion,
- knowledge-filer,
- capabilities-dokumentation,
- explicit lista över runtime-skillnader.

### Klart när

Custom GPT-versionen valideras utan att beteenderegler tappas bort.

---

## Steg 15 – Runtime parity och projekt-hygiene

### Mål

Säkerställa att Chat ZIP och Custom GPT följer samma kärnkontrakt.

### Kontroller

- kritiska regler finns i båda,
- samma delvalideringsprincip gäller,
- samma avståenderegel gäller,
- inga gamla temporära filer finns,
- genererade distributioner ligger inte bland canonical källor,
- status och dokumentation är uppdaterade.

### Klart när

parity- och hygiene-kontroller passerar eller endast har dokumenterade icke-blockerande varningar.

---

## Steg 16 – GitHub Actions CI och releasebygge

### Mål

Automatisera kvalitetssäkring och paketering.

### CI bör köra

- lint,
- schemas,
- unit tests,
- evals,
- project hygiene,
- build,
- distributionsvalidering.

### Release

GitHub Release-taggen ska styra versionsnumret i releaseartefakterna.

### Klart när

CI passerar och en testrelease kan bygga kompletta artefakter automatiskt.

---

## Steg 17 – Release candidate

### Mål

Skapa första kompletta RC-versionen.

### Leverans

- projekt-ZIP,
- Chat ZIP,
- Custom GPT-paket,
- checksummor,
- release-readiness-rapport,
- kända begränsningar.

### Klart när

inga blockerande valideringsfel återstår.

---

## Steg 18 – Stabil version 1.0

### Mål

Släppa en stabil första version efter praktisk Stud.io-verifiering.

### Release gate

- verifierade delar,
- fungerande LDraw-export,
- Stud.io-kompatibilitet,
- evals passerar,
- runtime parity bedömd,
- final project hygiene passerar,
- dokumenterade begränsningar är acceptabla.

---

# Möjliga funktioner efter version 1

Dessa ska inte blockera första releasen:

- verifiering av att del + färg faktiskt har producerats,
- BrickLink/Rebrickable-ID-mappning,
- användarens egen delsamling,
- begränsning till delar från ett visst set,
- kostnadsoptimering,
- minimering av ovanliga delar,
- mer avancerad kollisionsdetektion,
- connection-point-analys,
- stabilitetsanalys,
- Technic-konstruktioner,
- gångjärn och fria vinklar,
- automatiserad modellrendering,
- automatisk öppning/testning i Stud.io där tekniskt möjligt.

# Övergripande kvalitetsprincip

Den viktigaste invarianten för hela projektet är:

> En modell får aldrig levereras som verifierad om den innehåller en delreferens som inte kan bekräftas mot den auktoritativa katalogen.

När verifiering misslyckas ska systemet konstruera om, förenkla eller tydligt avstå.
