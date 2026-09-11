# Custom GPT-runtime

## Syfte

Custom GPT-distributionen ska bevara samma kärnkontrakt som Chat ZIP, men använder GPT Builder-konfiguration, Knowledge och Code Interpreter & Data Analysis i stället för en explicit lokal runtime med projektets Python-script.

## Rekommenderade capabilities

- **Code Interpreter & Data Analysis: PÅ (obligatorisk för full filgenerering)** – används för att skapa och returnera `.ldr`/`.mpd`-filer samt för strukturerad kontroll av genererad data.
- **Web search: AV som standard** – delkatalogen ska komma från den paketerade verifierade katalogen, inte från ad hoc-sökning på webben. Webbsökning kan aktiveras för kompletterande research men får aldrig användas som ersättning för kataloggaten.
- **Image generation: AV som standard** – inte nödvändig för kärnflödet.
- **Actions/Apps: inte nödvändiga i v1** – en framtida validator-Action kan ge starkare deterministisk parity med Chat-runtime.

## Knowledge-paket

Custom GPT-paketet laddar upp ett begränsat antal text-/JSON-filer som referensmaterial:

- verifierad delkatalog (`catalog/catalog.json`),
- schemas för tolkade krav, konstruktionsplan, intern modell och failure resolution,
- canonical referensdokument för konstruktion, validering, geometri, export och felhantering.

Knowledge är referensmaterial. Kritiska beteenderegler ligger därför kvar i `builder/instructions.md`.

## Runtimeflöde

1. Tolka användarens krav enligt instruktionen och schema-referensen.
2. Skapa konstruktionsplan.
3. Välj endast delreferenser som kan bekräftas i den paketerade katalogen.
4. Skapa intern modell.
5. Kontrollera schema, delreferenser, färgkoder, submodellgraf och konservativa geometriregler.
6. Vid blockerande fel: reparera enligt fallbackordningen eller avstå.
7. Använd Code Interpreter & Data Analysis för att serialisera den verifierade modellen till `.ldr` eller `.mpd` och lämna filen till användaren.

## Viktig parity-begränsning

Chat ZIP kan köra projektets deterministiska Python-validatorer direkt. En Custom GPT kan följa samma regler och använda Code Interpreter, men distributionen kan inte garantera att exakt samma lokala script exekveras som en obligatorisk runtime-gate i varje konversation. Därför ska Custom GPT-versionen beskrivas som **behavior-parity med reducerad execution-parity** tills en explicit Action eller annan deterministisk validator-tjänst finns.

Detta får aldrig mildra regeln om verifierade delar. Om katalogkontroll eller validering inte kan genomföras med tillräcklig säkerhet ska GPT:n avstå från att kalla modellen verifierad.
