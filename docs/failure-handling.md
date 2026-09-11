# Säker felhantering

## Syfte

En misslyckad konstruktion får aldrig repareras genom att modellen hittar på en del, delreferens, färg eller geometri. Ett valideringsfel är ett konstruktionsproblem som ska lösas genom ett nytt verifierbart förslag eller genom tydligt avstående.

## Obligatorisk fallbackordning

1. **Byt till annan verifierad del.** En ersättningsdel får endast väljas om dess exakta `.dat`-referens finns i den auktoritativa katalogen.
2. **Ändra konstruktionen.** Justera dimensioner, lager eller ortogonal orientering när geometri eller rotation inte passerar.
3. **Förenkla.** Minska sektionen, ta bort icke-kritisk detalj eller sänk detaljnivån.
4. **Avstå.** Om ett nytt förslag fortfarande inte passerar hela leveransgaten ska modellen rapporteras som ej verifierbar.

Varje reparationsförsök skapar ett nytt modellförslag som måste köra hela valideringskedjan från början. Ett reparationsbeslut i sig gör aldrig en modell levererbar.

## Maskinläsbar representation

`scripts/failure_handling.py` läser en valideringsrapport och skapar en plan enligt `schemas/failure-resolution.schema.json`.

Fältet `delivery_allowed` är alltid `false` när källrapporten är `fail`. `replacement_part` kan bara förekomma när kandidaten finns ordagrant i katalogens användbara modelldelar. Funktionen genererar aldrig egna partnummer.

## Begränsning

Version 1 reparerar inte godtycklig geometri automatiskt. Den producerar en säker, prioriterad reparationsplan som språkmodellen kan använda för att skapa ett nytt förslag. Detta är avsiktligt: deterministisk avhållsamhet är bättre än en automatisk men overifierbar reparation.
