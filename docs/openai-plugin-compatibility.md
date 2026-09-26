# OpenAI Plugin compatibility assessment

Projekt: **LEGO Modellbyggaren**  
GPT Byggaren: **1.5.0**  
Bedömning: **reduced / advisory-only / not active**

## Slutsats

OpenAI Plugin v1 ska inte aktiveras som peer distribution för LEGO Modellbyggaren i denna migrering.

Projektets canonical beteende kan representeras som skills och referensmaterial, men full funktionell parity kan inte bevisas för tre kritiska delar av kärnflödet:

1. **Persistent workspace/state** – `project-status.yaml` är auktoritativ tillståndskälla och ska kunna återupptas oberoende av chatthistorik.
2. **Deterministisk lokal validering** – verifierade modeller kräver att projektets faktiska validator körs och returnerar PASS; en ej körd kontroll får aldrig tolkas som PASS.
3. **Fail-closed artifact generation** – `.ldr`/`.mpd` får endast levereras efter godkänd validering, via den etablerade exportkedjan.

Plugin v1 är skills-first och ger inte i sig en garanti för dessa lokala exekverings- och workspaceegenskaper. Att paketera scripts som resurser skulle därför inte vara tillräckligt för att hävda equivalent runtime.

## Requirement parity

| Område | Bedömning | Motivering |
|---|---|---|
| Behavior | equivalent | Canonical regler och säkerhetsmarkörer kan uttryckas i en skill. |
| Capability | reduced | Analys och rådgivning kan bevaras, men verifierad modellproduktion kan inte garanteras. |
| Artifact | reduced | Filformaten kan beskrivas, men fail-closed generering kan inte garanteras av Plugin v1 ensam. |
| Workspace/state | reduced | Projektets persistenta filbaserade state kan inte göras till garanterad runtime-auktoritet. |
| Tool | reduced | Validator/export-scripts kan refereras eller paketeras, men faktisk obligatorisk exekvering kan inte garanteras. |

## Aktiveringsbeslut

- Status: `assessed_not_active`
- Compatibility: `reduced`
- Advisory only: `true`
- Ingen plugin-artifact ska byggas eller publiceras.
- OpenAI Plugin ska inte läggas till i `active_targets`.
- Release-artifact-setet ska förbli exakt härlett från nuvarande aktiva runtimes.

## Bevarade regler

Bedömningen ändrar inte:

- `assistant/instructions.md`,
- produktplan 18/18,
- VERSION `1.0.0-rc.2`,
- `VERIFIERADE DELAR ENDAST`,
- `STUDIO-KOMPATIBEL EXPORT`,
- `INGEN FALSK FYSIKGARANTI`,
- official LDraw release-catalog-gaten,
- manuell BrickLink Stud.io-status `not_run`,
- stable-release-statusen `blocked`.

## Framtida omprövning

Plugin kan omprövas om runtime senare kan ge explicit persistent workspace/state och obligatorisk deterministisk exekvering av projektets validator/exportkedja. Fram till dess är advisory-only den säkra beteendebevarande klassificeringen.
