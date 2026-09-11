# Release readiness – 1.0.0-rc.2

## Sammanfattning

LEGO Modellbyggaren 1.0.0-rc.2 är den första kompletta release candidate-versionen.
Alla automatiserade projekt-, runtime-, validerings-, eval-, parity- och distributionsgrindar är gröna i den lokala reproducerbara kedjan.

## Release gate

| Kontroll | Status | Kommentar |
|---|---|---|
| Canonical instruction/lint | PASS | Kritiska no-hallucination-regler finns kvar. |
| Intern modell och schemas | PASS | Giltiga/ogiltiga modeller testas. |
| Delkatalog | PASS | Fixture används lokalt; release workflow bygger `official_release` från LDraw `complete.zip`. |
| LDraw export | PASS | `.ldr` och `.mpd`, type-1-rader, submodeller och rotationer testas. |
| Statisk validering | PASS | Fail-closed leveransgate. |
| Konstruktionsstrategi | PASS | Konservativ och verifieringsdriven. |
| Kravtolkning | PASS | Svenska/engelska v1-fall testas. |
| Failure handling | PASS | Påhittade ersättningsdelar blockeras. |
| End-to-end | PASS | Textkrav till verifierad LDraw-fil testas. |
| Geometri v1 | PASS | Grid, höjd, ortogonal rotation och enkel collision testas. |
| Stud.io-formatkompatibilitet | PASS | Standard-LDraw-fall valideras automatiskt. |
| Stud.io GUI-import | NOT RUN | Måste köras i faktisk BrickLink Studio-installation före stabil 1.0. |
| Evals | PASS | 8/8 obligatoriska riskfall passerar. |
| Chat runtime self-test | PASS | Portabel runtime kan validera och exportera. |
| Custom GPT distribution | PASS | Builder-paketet håller instruktion/Knowledge-gränser. |
| Runtime parity | PASS | Full behavior parity; execution parity reducerad i Custom GPT enligt dokumentation. |
| Final hygiene | PASS | Inga blockerande temporära eller utvecklingsartefakter i runtime-paketen. |
| Release artifact verification | PASS | Version, ZIP-set, checksummor och leveransmanifest verifieras. |

## Blockerande fel

Inga blockerande automatiserade valideringsfel är kända för RC2.

## Återstående manuella releasekontroll

Före stabil 1.0 ska golden-filerna i `examples/studio-compatibility/` öppnas i BrickLink Studio och checklistan i `examples/studio-compatibility/manual-studio-results.md` fyllas i. Detta är en stabil-release-gate, inte ett blockerande fel för RC2.

## Katalognotering

Den lokala projektkällan använder en minimal fixture-katalog för reproducerbara tester. Den publicerade releasekedjan är konfigurerad att hämta LDraws officiella `complete.zip`, bygga `catalog/catalog.json` som `official_release` och köra samma tester/evals mot den fulla katalogen innan releaseartefakterna byggs.

## Beslut

**READY FOR RC: YES**

**READY FOR STABLE 1.0: NO – stable-release gate blocks until manual BrickLink Studio GUI verification has status `pass`.**
