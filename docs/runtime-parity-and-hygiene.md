# Runtime parity och projekt-hygiene

## Syfte

Chat ZIP och Custom GPT byggs från samma canonical beteendekontrakt men har olika exekveringsmiljöer. Detta steg skiljer därför uttryckligen mellan **behavior parity** och **execution parity**.

## Behavior parity

Följande kritiska regler måste finnas i canonical instruktion och båda runtime-målen:

- `VERIFIERADE DELAR ENDAST`
- `STUDIO-KOMPATIBEL EXPORT`
- `INGEN FALSK FYSIKGARANTI`

Chat ZIP använder canonical instruktion byte-identiskt. Custom GPT får använda deterministisk kompilering inom instruktionsgränsen, men får inte tappa kritiska beteendemarkörer eller flytta kärnbeteende till Knowledge.

## Execution parity

| Egenskap | Chat ZIP | Custom GPT |
|---|---|---|
| Canonical beteende | Full | Full |
| Katalog/schemas | Direkta runtime-filer | Knowledge-referenser |
| Deterministiska Python-validatorer | Full | Reducerad |
| Filgenerering | Lokal runtime | Code Interpreter/Data Analysis |
| Automatisk Stud.io-GUI-kontroll | Nej | Nej |

Custom GPT har därför **full behavior parity men reducerad execution parity** i version 1. En framtida extern validator-Action kan ge starkare execution parity.

## Versionsintegritet

`VERSION` i projektroten är default-källa för lokala byggen. Ett explicit `--version` får användas i CI/release och release-workflow använder GitHub Release-taggen. Alla runtime-`VERSION` och manifest måste matcha byggversionen.

Detta förhindrar att ett rent bygge efter rensning faller tillbaka till ett implicit `0.0.0-dev`.

## Hygiene-regler

Canonical projektkälla får inte bero på genererade `build/` eller `dist/`. Projekt-ZIP exkluderar alltid:

- `build/`
- `dist/`
- `.git/`
- Python-cache och testcache

Runtime-ZIP får dessutom inte innehålla utvecklingstester, evals, research, temporära filer eller cacheartefakter.

`project_hygiene.py --mode final --fix` används före releasebygge och `test_runtime_parity.py` används efter att båda runtime-målen har byggts.

## Gate

Steget passerar bara när:

1. kritiska beteendemarkörer finns i båda runtime-målen,
2. obligatoriska runtime-referenser finns,
3. versionsintegritet passerar,
4. inga förbjudna runtime-filer finns,
5. skillnaden i execution parity är explicit dokumenterad.
