# LEGO Modellbyggaren

## Syfte

Skapa en GPT som omvandlar en textuell beskrivning av ett LEGO-bygge till en verifierad LDraw-kompatibel modellfil för import i BrickLink Stud.io.

## Målbild

**Textbeskrivning → strukturerad konstruktion → verifierade delar → LDraw-export → Stud.io.**

GPT:n ska inte själv behöva producera färdiga PDF-bygginstruktioner. Stud.io används för visuell slutgranskning och Instruction Maker.

## Arkitekturprinciper

- `assistant/instructions.md` är canonical beteendekontrakt.
- En strukturerad intern modell införs före LDraw-serialisering.
- LDraw-biblioteket blir primär sanningskälla för delreferenser.
- Delvalidering är blockerande: overifierade delar får aldrig användas i en färdig verifierad modell.
- Chat ZIP och Custom GPT byggs från samma canonical beteende.

## Projektprofil

`zip_first_advanced`

## Viktiga avgränsningar för version 1

Ingen full fysiksimulering, ingen prisoptimering och ingen garanti att varje giltig LDraw-del/färg-kombination har funnits kommersiellt. Dessa kan utvecklas senare.

## Intern modellrepresentation

Version 1.0 av mellanformatet finns i `schemas/model.schema.json`. Positioner uttrycks i LDraw Units (LDU), rotationer som 3×3-matris och varje del bär separat status för katalog- och placeringsvalidering. Se `docs/internal-model.md` för mapping mot LDraw type-1-rader.
