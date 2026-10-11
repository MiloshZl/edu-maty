# EduPage – lokální studentský přehled

Rychlý návod: [Lokální spuštění](docs/SPUSTENI.md). Pro další vývoj: [projektový agent](AGENTS.md) a [kontext](docs/AGENT_CONTEXT.md).

Prototyp pro `spszl.edupage.org`: Python/FastAPI backend a React/TypeScript/Vite frontend. Slouží k ověření, která data umí studentský účet skutečně načíst. Uživatel potvrdil úspěšné načtení denního rozvrhu; ostatní živé funkce a úplná shoda dat se školním webem zůstávají **NEOVĚŘENO**. Demo obsahuje výhradně syntetická data a zapíná se samostatným tlačítkem.

## Spuštění nyní v tomto workspace (Windows / PowerShell)

Závislosti a lokální Python již byly připraveny. Otevřete dva terminály PowerShell.

**Terminál 1 – backend:**

```powershell
Set-Location 'C:\Users\krcma\maty-sklep-old\projekty\edupageMatyTest'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

**Terminál 2 – frontend:**

```powershell
Set-Location 'C:\Users\krcma\maty-sklep-old\projekty\edupageMatyTest\frontend'
npm.cmd run dev
```

Otevřete **http://127.0.0.1:5173**. Backend běží na http://127.0.0.1:8000; základní stav je na http://127.0.0.1:8000/api/health. Oba servery jsou vázané na loopback. Frontend volá `/api` přes Vite proxy; EduPage volá pouze backend.

1. Pro prohlídku rozhraní zvolte **Otevřít DEMO se syntetickými daty**. Nepotřebujete žádné údaje.
2. Pro živé napojení vyplňte vlastní studentské jméno a heslo do lokálního formuláře a zvolte **Přihlásit LIVE**. Škola je pevně omezená na `spszl`.
3. Po přihlášení se načte aktuální týden a zvolené pololetí. Jednotlivé funkce mohou mít různé stavy. Absence či suplování mohou být nepodporované, zatímco rozvrh je dostupný.
4. Po změně týdne, školního roku nebo pololetí stiskněte **Obnovit**. Obnovení má interval alespoň 10 sekund. Přepnutí záložek neprovádí vzdálené požadavky.
5. **Odhlásit** zruší lokální relaci, vymaže cache a zavře HTTP session. Pro vypnutí stiskněte **Ctrl+C v obou terminálech**.

Spuštění aplikace nespouští testy. Servery nejsou po dokončení práce automaticky ponechány spuštěné.

## Instalace na jiném počítači nebo obnova prostředí

Požadavky: Python **3.12** a Node.js **22.12+ nebo 24+** s npm. Prostředí `.venv` není přenositelné; po přesunu projektu ho vytvořte znovu. V tomto workspace je Python připravený také v `.runtime/python/cpython-3.12.12-windows-x86_64-none/python.exe`.

Ve složce projektu:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-lock.txt
Set-Location frontend
npm.cmd ci
```

Pokud nemáte příkaz `py`, použijte cestu ke svému `python.exe`. Zde můžete pro obnovu použít:

```powershell
.\.runtime\python\cpython-3.12.12-windows-x86_64-none\python.exe -m venv .venv
```

Není nutné aktivovat venv, upravovat PowerShell ExecutionPolicy ani používat Docker. Python závislosti jsou uzamčené v `backend/requirements-lock.txt`, frontend v `frontend/package-lock.json`.

### Linux / macOS

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-lock.txt
cd frontend
npm ci
cd ..
.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

Ve druhém terminálu ve složce `frontend`: `npm run dev`. Poté otevřete stejnou adresu http://127.0.0.1:5173.

## Co aplikace podporuje

- Osobní výsledný denní rozvrh: týden a detail dne, skupiny, časy, dvojhodiny a zrušené hodiny podle zdroje; aktuální/následující hodina a konec dne v Europe/Prague.
- Známky pro školní rok a pololetí, seskupené podle ID předmětu, s hodnotou, vahou, datem a komentářem. Rok je počáteční rok školního roku; pololetí 1/2 se převádí na knihovní `Term.FIRST` (`P1`) / `Term.SECOND` (`P2`). Výběr starších období není důkaz, že účet jejich data poskytuje.
- Simulátor známek a vah pouze v paměti frontendu. Vypočítává pouze podporované známky se známým započítáním a platnou vahou. Při neznámém započítání živých známek aplikace nevyrábí přesný průměr.
- Diagnostika každé funkce, neověřené období, chyby, částečný výsledek a zastaralá cache. Prázdný úspěšně načtený den se odlišuje od nedostupného dne.
- Demo absence s neznámým jmenovatelem; živá absence a podrobný osobní seznam suplování jsou výslovně nepodporované. Důvody viz `INTEGRATION_REPORT.md`.

## Relace a ochrana údajů

Heslo se po odeslání odstraní z pole a používá se pouze k přihlášení. Neukládá se na disk ani do webových úložišť. EduPage cookies a data jsou pouze v paměti backendu. Lokální neprůhledný token má HttpOnly cookie, SameSite=Strict, cestu `/api` a platnost jednu hodinu. Vypršelé relace se periodicky uvolňují. Po restartu backendu se musíte přihlásit znovu.

Cookie nemá `Secure`, protože tento prototyp používá lokální HTTP. Pro budoucí HTTPS je nutné nastavit `EDUPAGE_SECURE_COOKIE=1` a upravit pevný seznam povolených Origin pro konkrétní HTTPS frontend. Soubor `.env.example` je dokumentační ukázka; aplikace `.env` automaticky nenačítá. V PowerShellu se proměnná nastavuje přes `$env:EDUPAGE_SECURE_COOKIE = '1'`.

Mutující požadavky vyžadují Origin lokálního frontendu. CORS není otevřený, není implementovaná obecná proxy. Synchronní knihovna běží mimo async event loop a přístup k jedné relaci je serializovaný. Přihlášení je omezené na pět pokusů za minutu pro celý lokální backend.

Zprávy, odevzdávání úkolů, potvrzování známek, změny docházky a obědů aplikace nevolá. Vzdálené odhlášení se neprovádí; zavře se lokální HTTP session. CAPTCHA ani dokončení 2FA zatím nejsou podporované; aplikace zobrazí překážku. Samotné přihlášení na webu školy nepřenáší relaci do tohoto prototypu.

## Stav ověření

Před pokynem nepokračovat v testování prošlo 11 backendových testů, 3 frontendové testy výpočtů, TypeScript kontrola a produkční build původní verze frontendu. Následně byla aktualizována verze Vite na 8.3.4 a doplněna obsluha vypršení relací a dokumentace. **Konečný stav už nebyl znovu testován podle přání uživatele.** Automatický průchod prohlížečem nebyl proveden, protože žádný ovladatelný prohlížeč nebyl dostupný. Živé přihlášení se neprovádělo.
