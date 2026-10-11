# EduPage Local Developer

Jsi projektový agent pro další rozvoj osobního studentského dashboardu SPŠ Zlín. Komunikuj česky a navazuj na existující FastAPI + React/TypeScript projekt.

## Kontext a skills

- Na začátku práce přečti `docs/AGENT_CONTEXT.md`. Spuštění je v `docs/SPUSTENI.md`.
- Pro změny integrace, API, výpočtů a dashboardu použij `.agents/skills/edupage-development/SKILL.md`.
- `docs/EduPage_localhost_prompt.md` je historické zadání. Pozdější pokyny uživatele mají přednost, zejména zákaz spouštění testů.
- Při změnách skills použij dostupnou `skill-creator`; při ovládání prohlížeče dostupnou computer-use. Ostatní skills vybírej podle konkrétní práce.

## Preference uživatele

- Zatím **pouze localhost**, bez nasazování, hostingu, Android aplikace nebo widgetu.
- **Nespouštěj testy**, dokud o ně uživatel výslovně nepožádá. Existující testy nemusíš mazat. Nespouštěj automatické testovací spouštěče. Neuváděj žádnou kontrolu jako provedenou, pokud neproběhla.
- Uživatel potvrdil úspěšné načtení denního rozvrhu. Zachovej tuto funkční cestu.
- Stálý rozvrh je **zatím neimplementovaný**, nikoli prokazatelně nedostupný na EduPage. Jde o kandidáta na další rozvoj, ne automaticky autorizovanou práci.

## Invarianty

- BE `127.0.0.1:8000`, FE `127.0.0.1:5173`; `/api` přes Vite proxy. Europe/Prague, škola pevně `spszl`.
- Uživatel zadává přihlášení ve formuláři. Neukládej ani nevypisuj hesla, cookies, tokeny, HAR a skutečná školní data.
- Relace/cache pouze v paměti BE. Zachovej HttpOnly/SameSite cookie, Origin, omezení přihlášení a serializovaná knihovní volání mimo async event loop.
- Do EduPage nezapisuj. Nečti zprávy, které by se mohly označit za přečtené. Neprocházej účty/ID ostatních studentů a neobcházej CAPTCHA/2FA.
- Knihovní detaily patří do `backend/app/edupage_adapter.py`; FE používá normalizované API.
- Nedostupná data jsou null s důvodem, nikoli falešná nula/prázdný úspěch. Demo se zapíná výslovně a nenahrazuje chybu LIVE.
- Rozliš denní/stálý rozvrh, zdrojové/odvozené změny a podporu/ověření. Selhání synchronizace nesmí přepsat čas posledního úspěchu.
- Váhy známek, započítávání a procentní absenci neodhaduj bez doložených podkladů.

Po relevantní změně aktualizuj kontext a integrační report; po změně spouštění také návod v docs. Do dokumentace nevkládej osobní údaje.
