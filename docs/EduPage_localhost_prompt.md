# Prompt pro Codex: lokální ověření napojení EduPage

Jsi vývojář backendu a frontendu. V aktuálním workspace vytvoř a ověř malý funkční prototyp pro osobní studentský dashboard EduPage. Nezůstávej u návrhu: implementuj BE, FE, spusť dostupné kontroly a napiš přesný návod na lokální spuštění. Cílem je zjistit, jaká skutečná data dokážeme získat studentským účtem, a až potom vybrat finální architekturu.

## Kontext a rozsah

- Škola: Střední průmyslová škola Zlín.
- EduPage: https://spszl.edupage.org/ ; subdoména `spszl`.
- Přihlášení: běžné uživatelské jméno a heslo. Skutečné údaje zadá uživatel až do lokálního formuláře. Nevyžaduj je v chatu ani v zadání.
- Priorita: osobní rozvrh a suplování.
- Dále: známky, vážené průměry, simulátor budoucích známek, celková absence a procentní absence v předmětech.
- Finálně může vzniknout Android aplikace s widgetem pro rozvrh a suplování; ostatní funkce mohou zůstat na webu. Android ani widget v této fázi nevytvářej.
- Prototyp běží pouze na localhostu. Bez nasazování, externí databáze, push notifikací a více uživatelů.
- Nezapisuj nic do EduPage. Neposílej zprávy, neodevzdávej úkoly, nepotvrzuj známky, neměň docházku ani objednávky. Pozor: i načtení některých stránek může označit zprávy za přečtené; zprávy nejsou součástí tohoto prototypu.

## 1. Prozkoumej prostředí a ověř knihovnu

Nejprve přečti platné AGENTS.md a prozkoumej současný projekt. V existujícím repozitáři zachovej jeho konvence a změny uživatele. Nevytvářej nový projekt přes existující soubory. V prázdném workspace použij strukturu uvedenou níže.

Výchozí stack:

- BE: Python + FastAPI + knihovna `edupage-api`.
- FE: React + TypeScript + Vite.
- Časové pásmo: Europe/Prague, české prostředí.
- BE na `127.0.0.1:8000`; FE na `127.0.0.1:5173`.
- Vite proxy `/api` na backend. Prohlížeč nikdy nevolá EduPage přímo.
- Nepoužívej Docker jako nutnou podmínku. Připrav návod pro Windows/PowerShell; doplň stručné příkazy pro Linux/macOS.

Referenční projekty:

- https://github.com/EdupageAPI/edupage-api
- https://github.com/loumadev/EdupageAPI
- https://edupageapi.github.io/edupage-api/

Jde o neoficiální projekty. Před použitím ověř aktuální zdrojový kód, verzi, licenci a skutečné signatury metod. Nehádej názvy endpointů či metod podle starých příkladů. Zaznamenej konkrétní použitou verzi; závislosti uzamkni vhodným lockfile nebo přesnými verzemi.

Pokud knihovna neumí část dat, prověř minimální vlastní adaptér nad oprávněnými požadavky studentského webového klienta. Odliš chybu parsování, chybějící implementaci a nedostatečná oprávnění. Nezkoušej jiné účty, neprocházej ID ostatních studentů, neobcházej CAPTCHA ani 2FA. Při jejich požadavku zobraz konkrétní stav a popiš podporovanou cestu dokončení; pokud ji nelze implementovat, ponech ji jako zdokumentované omezení.

Pokud není přístup k internetu nebo přihlašovací údaje, dokonči aplikaci, izolované testy a návod. Živé napojení označ jako NEOVĚŘENO, nikoli jako funkční. Testovací data smějí sloužit pouze explicitně označenému demo režimu.

## 2. Malá, přehledná struktura

Preferuj:

```text
backend/
  app/main.py
  app/edupage_adapter.py
  app/models.py
  app/calculations.py
  tests/
  .env.example
  requirements.txt nebo pyproject.toml + lockfile
frontend/
  src/
  package.json
  lockfile
README.md
INTEGRATION_REPORT.md
.gitignore
```

Nezaváděj zbytečné vrstvy ani mikroslužby. Veškeré detaily knihovny a formátu EduPage izoluj v adaptéru. FE musí používat normalizovaný datový model tvého backendu, nikoli syrové odpovědi EduPage. Synchronní HTTP volání knihovny nenech blokovat async event loop; volání stejné relace serializuj, pokud knihovna nezaručuje thread safety.

## 3. Přihlášení a lokální relace

- FE formulář: uživatelské jméno, heslo; škola přednastavená na `spszl` a v BE pevně omezená na tuto doménu.
- Heslo používej jen pro založení relace, po pokusu ho zahoď; v FE po odeslání vymaž pole. Neukládej ho na disk, do databáze, localStorage, sessionStorage ani do cookies.
- EduPage cookies, tokeny a relaci drž pouze v paměti BE. Po restartu BE se uživatel přihlásí znovu.
- Pro FE vytvoř vlastní náhodný neprůhledný session token v HttpOnly cookie, SameSite=Strict, omezené platnosti. V lokálním HTTP režimu vysvětli výjimku ze Secure; pro budoucí HTTPS musí být Secure zapnuto.
- Kontroluj Origin u mutujících požadavků, neumožňuj libovolný CORS a nezpřístupňuj službu na `0.0.0.0`. Nezaváděj obecný HTTP proxy endpoint.
- Chraň login před opakovaným rychlým zkoušením a synchronizaci před souběhem. Po chybě přihlášení automaticky neopakuj pokusy v nekonečné smyčce.
- Odhlášení zruší lokální relaci, paměťovou cache a zavře HTTP session; vzdálené odhlášení proveď jen pokud má knihovna ověřenou podporu.
- Nikdy neloguj hesla, cookies, tokeny, login body ani syrové odpovědi obsahující osobní údaje. Do repozitáře nepřidávej HAR, skutečné známky ani docházku.

## 4. Navržené vlastní API

Implementuj tyto cesty nebo zdůvodni drobnou úpravu:

```text
GET  /api/health
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/status
GET  /api/capabilities
POST /api/sync
GET  /api/timetable?from=YYYY-MM-DD&to=YYYY-MM-DD
GET  /api/substitutions?from=YYYY-MM-DD&to=YYYY-MM-DD
GET  /api/grades?schoolYear=...&term=...
GET  /api/attendance?schoolYear=...&term=...
```

Tohle jsou endpointy našeho BE, nikoli tvrzení o oficiálním API EduPage. Validuj rozsahy dat a maximální rozsah požadavku. Pojmenování školního roku a pololetí převeď podle ověřeného formátu knihovny.

Odpovědi nesou stav, zdroj dat, období a čas posledního úspěšného načtení. Rozliš stavy `ok`, `partial`, `unsupported`, `error` a `not_verified`; `stale` uveď jako samostatný příznak. U funkcí vracej `liveVerified`, bezpečnou stručnou příčinu a případná omezení. Čas posledního pokusu nesmí přepsat čas poslední úspěšné synchronizace.

Nedostupná data nevracej jako nulu nebo prázdný seznam, který vypadá jako úspěšný výsledek. Skutečně ověřený prázdný výsledek má být od nedostupnosti rozlišitelný. Chyby klientovi neposílej jako syrový traceback.

## 5. Rozvrh a suplování — hlavní priorita

Načítej osobní rozvrh přihlášeného studenta včetně jeho skupin. Rozliš stálý rozvrh a skutečný rozvrh konkrétního dne. Připrav pohled týdne a detail dne; automaticky otevři aktuální týden.

Normalizovaná hodina má datum, pořadí, začátek/konec, ID a název předmětu, učitele, učebnu, skupinu, stav změny a dostupné původní hodnoty. Neznámé hodnoty jsou null, nevymýšlej je. Použij stabilní zdrojové ID, případně zdokumentovaný složený klíč.

Zvýrazni změnu učitele, učebny či předmětu, zrušení, přesun a přidanou hodinu, pokud zdroj tyto informace skutečně poskytuje. Původní a novou hodnotu ukaž pouze pokud jsou obě dostupné. Pokud knihovna poskytuje pouze výsledný denní rozvrh, označ omezení detailů suplování. Porovnání se stálým rozvrhem může být odvozená změna, nikoli automaticky potvrzené suplování.

Zobraz aktuální/následující hodinu a konec výuky. Prázdniny a volné dny nesmějí vypadat jako chyba napojení. Otestuj dvojhodiny, půlnoc a český čas. Při změně času zachovej správné lokální datum.

## 6. Známky, průměry a simulátor

- Seskupuj známky podle stabilního ID předmětu; podporuj výběr pololetí a roku podle dostupných dat.
- Zobraz hodnotu, váhu, datum, název hodnocení a případný komentář.
- Pro podporované běžné známky počítej `sum(value * weight) / sum(weight)` z nezakrouhlených hodnot; zaokrouhli až výsledek pro zobrazení.
- Ověř význam a měřítko vah z knihovny. Nesměšuj váhu s maximálním počtem bodů. Chybějící váhu nenahrazuj potichu jedničkou.
- Body, procenta, slovní hodnocení, plus/minus, nezapočítané známky a kategorie nepřeváděj svévolně na stupnici 1–5. Zobraz je a vysvětli dopad na výpočet. Pokud průměr nelze věrně reprodukovat, ukaž omezení. Případný průměr přímo ze zdroje zobraz odděleně od vlastního výpočtu.
- Simulátor umožní přidávat/odebírat hypotetické známky a váhy, ukáže původní a nový průměr. Tyto změny existují jen ve FE, nezapisují se do EduPage a nevyvolávají vzdálené požadavky.
- Označ: simulace průměru není záruka známky na vysvědčení. Automatické hranice klasifikace nevymýšlej.

## 7. Absence — ověřit dostupnost, nevyrábět přesnost

Prověř, zda lze získat souhrn absence, omluvené/neomluvené hodiny, absenci v předmětech a počet skutečně uskutečněných započítávaných hodin ve stejném období.

Výpočet pro předmět: `zameškané hodiny / uskutečněné započítávané hodiny * 100`.
Celkové procento: poměr součtů hodin, nikoli průměr procent předmětů. Při nulovém či neznámém jmenovateli je výsledek null.

Preferuj oficiální souhrn dostupný účtu nebo skutečné historické údaje výuky a docházky. Budoucí hodiny ani opakování týdenního rozvrhu nepoužívej pro přesné aktuální procento. Pokud takový model nabídneš, odděl jej jako odhad; pro MVP jej lze vynechat.

Zameškané a uskutečněné hodiny musí mít stejné jednotky a období. Prověř význam školních akcí, zrušených hodin, suplování, dělených skupin a pozdních příchodů. Pokud potřebná data nelze získat, zobraz známé počty a stav „Procento nelze z dostupných dat spolehlivě určit“. Chybějící absenci neoznač jako 0 %.

## 8. Frontend pro skutečné ověření

Vytvoř jednoduché přehledné mobilně použitelné rozhraní s českými texty:

1. Přihlášení a stav relace.
2. Rozvrh a suplování jako hlavní obrazovka.
3. Známky s průměry a simulátorem.
4. Absence.
5. Diagnostika dostupnosti funkcí.

V horní části zobraz režim LIVE/DEMO, poslední úspěšnou synchronizaci a tlačítko Obnovit. Prototyp nemá automaticky pollovat EduPage; synchronizaci prováděj při přihlášení a výslovném obnovení, s paměťovou cache a omezením rychlých opakovaných požadavků. Změna záložky nemá zbytečně opakovat stejné požadavky.

Implementuj stavy načítání, částečného úspěchu, vypršení relace, nedostupné funkce, skutečně prázdných dat a zastaralé cache. Chyba absence nesmí shodit rozvrh ani známky. Nevkládej vzdálené HTML bez sanitizace a nepoužívej eval. Zachovej čitelnost a přístupnost; vzhled neupřednostňuj před ověřením dat.

Demo režim má být explicitně volitelný, má vlastní deterministická syntetická data a nikdy se neaktivuje potichu po chybě živého napojení. Je užitečný pro UI a testy, ne jako důkaz integrace.

## 9. Testy a ověření

Proveď smysluplné automatické testy:

- Vážené průměry a simulace, chybějící/invalidní váhy a nepodporované typy hodnocení.
- Absence: nulový jmenovatel, neznámý počet výuky, celkový poměr součtů a rozdílná období.
- Adaptér: úspěšná, prázdná, neúplná a změněná odpověď na syntetických fixtures; fixtures nesmí obsahovat osobní údaje.
- API: nepřihlášený přístup, logout, izolace relace a částečné selhání synchronizace.
- Rozvrh: zrušená hodina, dělené skupiny, lokální datum a odvozené versus zdrojově potvrzené změny.

Spusť backend testy, TypeScript kontrolu a produkční build FE. Pokud je dostupný prohlížeč, ověř průchod UI v demo režimu. Živé přihlášení neprováděj bez lokálně zadaných údajů uživatele. Neoznač mock testy za úspěšný živý integrační test.

## 10. Dokumentace a podmínky dokončení

V README.md uveď přesné příkazy pro instalaci, start BE a FE, adresy aplikace, zadání údajů, demo režim a postup vypnutí. Nepředpokládej Unix aktivaci venv na Windows; nabídni spouštění pomocí konkrétního python.exe ve venv. Zdokumentuj, že oba procesy jsou vázané na loopback a že relace po restartu zaniká.

Do INTEGRATION_REPORT.md napiš:

- Použitou knihovnu, přesnou verzi, zdroj, licenci a případné vlastní úpravy.
- Tabulku funkcí: rozvrh, osobní skupiny, suplování, známky/váhy, celková absence, absence po předmětech, počet uskutečněných hodin.
- U každé funkce odděl podporu v kódu, automatické ověření a skutečné živé ověření na SPŠ Zlín.
- Známá omezení a chybějící data; technickou příčinu, pokud je doložená.
- Manuální checklist: porovnat konkrétní den se suplováním, osobní skupinu, předmět se známkami různých vah a absenci ve stejném pololetí s EduPage.
- Doporučení pro další krok až podle výsledků: zachovat knihovnu, opravit adaptér, nebo změnit cestu napojení. Finální hosting ani Android synchronizaci teď nerozhoduj.

MVP je hotové, když lze lokálně spustit BE/FE, zadat vlastní údaje, spustit kontrolu napojení a vidět pravdivé stavy jednotlivých funkcí. Pokud nefunguje login nebo některá data, zachovej funkční diagnostiku a přesně popiš překážku; nenahrazuj výsledek vymyšlenými daty.

Na konci stručně napiš, co bylo implementováno, co prošlo testy, co zůstává neověřeno a jak prototyp spustit. Nezastavuj práci po samotném návrhu. Pokud práce vyžaduje interaktivní zadání přihlášení, dokonči vše ostatní a předlož uživateli konkrétní připravenou aplikaci k lokálnímu testu.
