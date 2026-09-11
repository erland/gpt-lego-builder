# Evals och regressioner

## Syfte

Evalsviten är en separat kvalitetsgrind som testar de viktigaste produkt-riskerna över flera komponenter samtidigt. Den kompletterar unit- och schema-testerna.

## Obligatoriska riskkategorier

- `hallucinated_parts`: okända eller påhittade delreferenser får aldrig bli levererbara.
- `invalid_ldraw`: exporterad LDraw ska följa förväntad type-1-struktur.
- `requirement_retention`: uttryckliga användarkrav som delbudget, färg och dimension får inte tappas bort.
- `part_budget`: modeller som överskrider `max_parts` ska blockeras.
- `vague_prompt`: saknade icke-kritiska detaljer ska härledas konservativt utan onödiga blockerande frågor.
- `correct_abstention`: när en blockerande konflikt saknar verifierad lösning ska systemet avstå.

## Release gate

Alla evalfall med `required: true` måste passera. Ett misslyckat obligatoriskt evalfall blockerar CI och release.

Resultatet skrivs till `evals/results.json` när sviten körs lokalt eller i CI.
