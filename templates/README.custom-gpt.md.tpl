# {{GPT_NAME}} – Custom GPT-distribution

Detta paket innehåller Builder-underlaget för **{{GPT_NAME}}**.

## Installera

1. Öppna GPT Builder.
2. Klistra in innehållet i `builder/instructions.md`.
3. Lägg in startprompterna från `builder/conversation-starters.md`.
4. Aktivera capabilities enligt `builder/capabilities.md` – **Code Interpreter & Data Analysis krävs för full filgenerering**.
5. Ladda upp samtliga filer i `builder/knowledge-package/` som Knowledge.
6. Läs `COMPATIBILITY.md` och `CUSTOM-GPT-RUNTIME.md`.
7. Testa minst ett positivt och ett negativt scenario i Preview innan GPT:n delas.

## Viktigt om katalogen

Om `builder/knowledge-package/catalog/catalog.json` är märkt som `fixture` är paketet endast ett utvecklingsbygge. Det får inte användas för att påstå full katalogverifiering av godtyckliga användarmodeller. Produktionsrelease ska innehålla en `official_release`-katalog.

## Version

{{VERSION}}
