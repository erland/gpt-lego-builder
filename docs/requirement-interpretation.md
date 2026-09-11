# Kravtolkning – fri text till strukturerade byggkrav

## Syfte

Steg 10 definierar hur fri text normaliseras innan konstruktionsplanen skapas. Målet är att användaren ska kunna beskriva modellen naturligt utan LDraw- eller schema-kunskap.

## Grundprincip

Tolkningen ska skilja på tre typer av information:

1. **uttryckliga krav** – sådant användaren faktiskt har angett,
2. **härledda standarder** – konservativa val som inte väsentligt ändrar avsikten,
3. **öppna frågor** – endast designval som inte rimligen kan härledas utan risk att ändra användarens avsikt.

Utdata följer `schemas/interpreted-request.schema.json`.

## V1-stöd

Tolkaren känner igen bland annat:

- motiv/ämne,
- displaymodell kontra leksaksmodell,
- `simple`, `balanced` och `detailed`,
- maximal delbudget,
- explicit färg när färgen finns i aktuell LDraw-katalog,
- dimensioner som `12 x 8 x 10 studs`,
- enskild bredd/längd/höjd i studs,
- svenska och engelska grundformuleringar.

## Härledda standarder

När storlek saknas används ett konservativt start-envelope per grov motivklass:

- fordon: 10 x 20 x 8 studs,
- byggnad: 20 x 16 x 16 studs,
- möbel: 12 x 8 x 10 studs,
- djur/figur: 10 x 16 x 12 studs,
- generiskt objekt: 12 x 16 x 12 studs.

När detaljnivå saknas används `balanced`.

När färg saknas väljer konstruktionssteget senare ett fåtal kataloggiltiga färger. Ingen färgidentitet får hittas på.

## När GPT:n ska fråga

GPT:n ska inte fråga bara för att något är ospecificerat. Den ska fråga först när ett verkligt designval inte går att härleda säkert.

Exempel på blockerande fråga i v1:

- `Bygg en stuga som är 15 cm.`

En ensam fysisk längd kan avse bredd, djup eller höjd. Att välja fel axel kan ändra hela modellens skala och proportioner, så detta ska markeras som en blockerande öppen fråga.

Däremot ska följande inte kräva frågor:

- `Bygg en katt.` → härled balanserad detaljnivå och rimlig standardstorlek.
- `Bygg en röd traktor, cirka 20 studs lång.` → använd explicit längd och härled övriga dimensioner.
- `Bygg ett enkelt bord.` → använd enkel detaljnivå och standard-envelope för möbel.

## Determinism

Samma prompt, katalogversion och tolkarversion ska ge samma strukturerade krav. Reglerna är därför explicita och utan slumpmässiga val.

## Begränsningar

Detta är en konservativ v1-tolkare, inte en full språkförståelsemotor. Komplexa proportioner, flera alternativa storlekar, ovanliga färgnamn och motsägelsefulla krav kan behöva hanteras i senare steg eller som öppna frågor.
