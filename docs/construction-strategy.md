# Konstruktionsstrategi – text till LEGO-geometri

## Syfte

Detta dokument definierar den reproducerbara strategi som LEGO Modellbyggaren ska följa innan den interna modellen skapas. Strategin är konservativ: den prioriterar verifierbarhet, enkel geometri och vanliga kopplingsmönster framför avancerade eller spekulativa byggtekniker.

## Beslutsordning

När flera lösningar uppfyller användarens mål ska de prioriteras i följande ordning:

1. verifierad delreferens och giltig LDraw-färg,
2. enkel ortogonal geometri,
3. tydlig bärande struktur,
4. få olika deltyper och återanvändning av vanliga delar,
5. användarens storleks- och delbegränsningar,
6. visuell likhet och detaljrikedom,
7. avancerade tekniker endast när enklare lösningar inte räcker.

En estetiskt bättre lösning får aldrig vinna över en verifierbar lösning om den kräver en overifierad del eller placering.

## Arbetsflöde

### 1. Tolka designmålet

Normalisera först fri text enligt `docs/requirement-interpretation.md` och `schemas/interpreted-request.schema.json`. Extrahera därefter följande från användarens text:

- motiv eller objekt,
- funktion kontra displaymodell,
- önskad ungefärlig storlek,
- färger,
- detaljnivå,
- maximalt delantal,
- uttryckliga konstruktionskrav,
- uttryckliga förbud eller begränsningar.

När ett värde saknas ska en konservativ standard härledas i stället för att fråga, så länge valet inte ändrar användarens avsikt väsentligt.

### 2. Bestäm skala och målvolym

Översätt motivet till ett ungefärligt LEGO-envelope i studs. Börja hellre något större och enklare än för litet och överdetaljerat.

Riktlinjer:

- `simple`: prioritera siluett och igenkänning,
- `balanced`: prioritera siluett plus några karakteristiska detaljer,
- `detailed`: fler sektioner och detaljer, men fortfarande konservativ geometri.

Dimensioner behöver inte vara exakta innan den faktiska delplaceringen är klar. Slutliga LDU-dimensioner ska komma från den interna modellen.

### 3. Identifiera huvudvolymer

Bryt motivet i 2–7 huvudvolymer eller funktionella sektioner. Exempel:

- fordon: chassi, kaross, kabin, hjul/axelområden, detaljer,
- byggnad: grund, väggar, tak, öppningar, detaljer,
- möbel: ben/stöd, skiva/kropp, förstärkning, detaljer,
- figur/djur: torso/kärna, huvud, lemmar, svans/utstickande delar, detaljer.

Sektionerna ska kunna byggas i en tydlig ordning från bärande struktur till detaljer.

### 4. Välj konstruktionsteknik per sektion

Version 1 ska i första hand använda:

- studs-up stapling,
- plates för höjdjustering och lager,
- bricks för bärande volym,
- tiles/slopes endast när de finns verifierade och placeringen är enkel,
- ortogonala 90-graders rotationer när rotation behövs.

Undvik som standard:

- clips/bars med fria vinklar,
- flex-delar,
- slangar,
- komplex Technic-geometri,
- gångjärn i icke-ortogonala vinklar,
- SNOT-kopplingar som kräver exakt connection-point-resonemang,
- delar vars funktion eller orientering inte kan motiveras säkert.

Sådana tekniker kan introduceras senare när geometri- och connection-validering stöder dem.

### 5. Välj kandidater ur katalogen

Delar ska väljas från den tillgängliga auktoritativa katalogen, aldrig från modellens minne av ett möjligt artikelnummer.

Urvalet ska föredra:

1. delar som redan används i modellen,
2. grundläggande bricks/plates/tiles med enkel orientering,
3. färger som användaren efterfrågat och som finns i LDraw-färgkatalogen,
4. en liten uppsättning deltyper framför många specialdelar.

Om katalogen inte innehåller en lämplig del ska konstruktionen ändras, inte delnumret uppfinnas.

### 6. Bygg bärande struktur först

Skapa modellens kärna i denna ordning:

1. bas eller primärt stöd,
2. bärande volymer,
3. sammanbindande lager,
4. sekundära volymer,
5. ytskikt,
6. karakteristiska detaljer.

Detaljer som inte påverkar igenkänning får tas bort först om `max_parts` överskrids.

### 7. Skapa strukturerad konstruktionsplan

Innan intern modell skapas ska planen följa `schemas/construction-plan.schema.json`. Den ska dokumentera:

- tolkade krav,
- härledda antaganden,
- målvolym,
- sektioner,
- vald teknik per sektion,
- byggordning,
- fallback-regler.

Planen är ett arbetsunderlag och inte ett verifieringsbevis.

### 8. Skapa intern modell

Översätt planen till `schemas/model.schema.json`:

- varje fysisk del får ett unikt `instance_id`,
- varje delreferens ska finnas i katalogen,
- placering anges i LDU,
- rotation anges som proper ortonormal 3×3-matris,
- submodeller används endast när de gör modellen tydligare eller återanvändbar.

### 9. Validera och omkonstruera

Kör statisk validering. Vid fel används denna fallbackordning:

1. ersätt med annan verifierad del,
2. ändra dimension eller lagerindelning,
3. förenkla den berörda sektionen,
4. ta bort icke-kritisk detalj,
5. minska detaljnivån,
6. rapportera att kravet inte kan verifieras.

Samma fel får inte lösas genom att kringgå validatorn.

## Standarder när användaren inte specificerar allt

Dessa är startpunkter, inte hårda regler:

- detaljnivå: `balanced`,
- max_parts: ingen hård gräns om användaren inte anger en,
- rotationsstil: ortogonal,
- byggteknik: studs-up,
- antal huvudsektioner: 2–7,
- färg: behåll motivets naturliga färgidé om den är tydlig; annars använd få färger,
- submodeller: endast när de ger faktisk struktur eller återanvändning.

## Reproducerbarhet

Två körningar med samma krav och samma katalogversion bör fatta samma övergripande beslut. Därför ska GPT:n:

- följa beslutsordningen ovan,
- undvika slumpmässiga partnummer,
- undvika att byta konstruktionsteknik utan kravskäl,
- dokumentera härledda antaganden i konstruktionsplanen,
- föredra den enklare av två likvärdiga lösningar.

## Version 1-begränsning

Strategin gör modellen mer konsekvent men bevisar inte fysisk byggbarhet. Connection points, kollisioner och stabilitet får fortfarande vara `pending` tills senare valideringssteg kan kontrollera dem.
