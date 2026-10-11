---
name: edupage-development
description: "Rozvíjej lokální EduPage dashboard tohoto projektu: FastAPI adaptér, normalizované API, React UI a školní výpočty. Použij pro změny tohoto workspace a jeho EduPage integrace."
---

# EduPage development

Přečti kořenový `AGENTS.md` a `docs/AGENT_CONTEXT.md`. Aktuální zadání určuje rozsah; návrhy dalšího rozvoje nejsou samostatnou autorizací.

## Integrace

- Ověř signatury/pole v instalovaném `edupage-api` ve `.venv/Lib/site-packages/edupage_api`; online zdroje porovnej s připnutou verzí. Neupravuj přímo venv, změny izoluj v adaptéru.
- Pro stálý rozvrh prověř rozdíl `get_my_timetable` / `get_timetable` a původní pole před parserem. `showOrig=true` není důkaz dostupnosti stálého rozvrhu. Zachovej funkční denní cestu a dotazy jen na vlastní účet.
- Před vlastním HTTP voláním dolož jeho read-only význam ze zdroje nebo oprávněného studentského klienta. Neodhaduj endpointy/ID a neukládej osobní odpovědi či autentizační data.
- Zachovej obálku `status`, `source`, `period`, `data`, `lastSuccess`, `lastAttempt`, `stale`, `liveVerified`, `reason`, `limitations`. Prázdný úspěch není nedostupnost. `unsupported` označuje naši implementaci, ne automaticky nemožnost na EduPage.
- Zdrojovou změnu potvrď jen doloženým příznakem; odvozené porovnání označ odděleně. Stálý rozvrh potřebuje platnost a osobní skupiny, jeden den není základní týden.

## Výpočty a UI

- Průměr jen pro podporovanou číselnou známku, platnou kladnou váhu a známé započítání. Nezaokrouhluj mezivýsledky a svévolně nepřeváděj body/procenta/plus-minus.
- Absence potřebuje stejné období a jednotky čitatele/jmenovatele. Celkové procento je poměr součtů; neznámý/nulový jmenovatel je null.
- Datum určuj v Europe/Prague; pozor na UTC půlnoc/DST a knihovní ztrátu `24:00` → `23:59`.
- FE používá jen naše `/api`, nepolluje EduPage, simulace nevolá backend. Zachovej výslovné DEMO, české stavy a nezávislost funkcí při chybě.

## Dokončení

Dodrž zákaz spouštění testů z `AGENTS.md`. Změny zkontroluj čtením a neoznač je za otestované. Aktualizuj integrační report a kontext při změně schopností/omezení/evidence. Návod je v `docs/SPUSTENI.md`. Uveď výsledné chování a neověřená místa.
