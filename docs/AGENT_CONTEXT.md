# Kontext pro další rozvoj

Aktualizováno 11. 10. 2026. Jde o předání faktů a rozhodnutí dalšímu agentovi, nikoli úkoly k automatickému provedení.

## Rozsah

Studentský dashboard SPŠ Zlín (`spszl.edupage.org`). Priorita: rozvrh a suplování. Dále známky, průměry, lokální simulace a absence. Uživatel chce zatím localhost a nechce spouštět testy. Hosting, Android, widget, push a externí databáze nejsou aktuální zadání.

## Architektura

| Soubor | Úloha |
| --- | --- |
| `backend/app/main.py` | API, relace, Origin, cache, synchronizace, limity a vypršení |
| `backend/app/edupage_adapter.py` | Knihovna, login, normalizace, bezpečné chyby a explicitní demo |
| `backend/app/models.py` | Vstup přihlášení a obálka výsledku |
| `backend/app/calculations.py` | Průměry, absence a aktuální hodina v Europe/Prague |
| `frontend/src/main.tsx` | České přihlášení, rozvrh, známky, simulátor, absence a diagnostika |
| `frontend/src/calculations.js` | Simulace a lokální datum/týden |
| `frontend/src/style.css` | Responzivní UI |
| `frontend/vite.config.ts` | Loopback a proxy `/api` |
| `backend/requirements-lock.txt`, `frontend/package-lock.json` | Uzamčené závislosti |
| `docs/SPUSTENI.md` | Návod ke spuštění |
| `INTEGRATION_REPORT.md` | Evidence podpory a omezení |

Stack: Python 3.12, FastAPI 0.115.12, edupage-api 0.13.1, React 19.1.0, TypeScript 5.8.3, Vite 8.3.4. Lokálně byly připraveny `.venv`, `.runtime/python`, `frontend/node_modules`. Workspace původně nebyl Git repozitář; před Git operacemi ověř aktuální stav.

API: health; auth login/logout/status; capabilities; sync; timetable/substitutions s `from`/`to`; grades/attendance s `schoolYear`/`term`. GET čte cache, login a POST sync načítají data. Max. rozsah 14 dní, relace hodinu, sync po 10 sekundách. Origin mutací musí být `http://127.0.0.1:5173` nebo `http://localhost:5173`.

## Stav integrace

- **Uživatel potvrdil úspěšné načtení denního rozvrhu.** Jde o uživatelské potvrzení načtení, ne nezávislé srovnání každé hodiny a skupiny.
- Agent nepoužil skutečné přihlašovací údaje. Známky, váhy, absence a podrobné suplování tím nejsou ověřené.
- `get_my_timetable(date)` vrací denní výsledný plán. Skupiny/zrušení jsou `Lesson.groups` / `Lesson.is_cancelled`.
- **Stálý rozvrh zatím není implementovaný.** Text UI „Stálý rozvrh ... nejsou dostupné“ je příliš kategorický. Při budoucí změně používej „zatím neimplementováno“, dokud není doložené omezení zdroje.
- Jiná knihovní cesta `get_timetable(target, date)` má interní `showOrig=true`, ale parser `Lesson` původní hodnoty nezachovává. Je to vodítko k průzkumu, nikoli důkaz dostupnosti stálého týdne nebo jednoduchého přepnutí parametru.
- Nezrušené LIVE hodiny mají změnu `unknown`, ne potvrzeně nezměněno. Klíč datum/pořadí/index není dlouhodobě stabilní při přeuspořádání odpovědi.
- Známky používají `get_grades_for_term(year, Term.FIRST/SECOND)`. Rok je počáteční rok, term `P1`/`P2`. Běžná váha = `p_vaha / 20`; bodové maximum není váha. Započítání a kategorie nejsou spolehlivě dostupné, LIVE položky mají `included=null` a vlastní průměr zůstává neurčený.
- Živá absence a osobní podrobnosti suplování jsou `unsupported`. Vlastní adaptéry nejsou implementované. Neznámý jmenovatel absence nenahrazuj opakováním rozvrhu.
- CAPTCHA/2FA jsou rozpoznány jako překážka, dokončení není implementované. Logout je pouze lokální.

## Dřívější kontroly

Před zákazem testů prošlo 11 BE testů, 3 FE testy výpočtů, TypeScript a build s původním Vite. Poté se změnilo Vite na 8.3.4, uvolnění relací, izolace chyb funkcí a obsluha vypršení ve FE. Konečný stav nebyl znovu testován. Instalace opraveného Vite oznámila nula zranitelností. Starší `frontend/dist` může být neaktuální; používej `npm run dev` podle návodu.

Ovladatelný prohlížeč při tvorbě nebyl dostupný, agent UI průchod neověřil. Dostupnost nástrojů se může změnit. Tyto historické údaje nejsou pokynem testy znovu spustit.

## Kandidáti na další rozvoj na vyžádání

1. Upřesnit hlášku a doplnit stálý osobní rozvrh z doloženého zdroje včetně platnosti a skupin.
2. Zachovat původní/nové hodnoty suplování jen pokud jsou dostupné a spojitelné s vlastní hodinou.
3. Ověřit započítání a kategorie známek.
4. Prověřit studentský souhrn absence a skutečný jmenovatel za stejné období.

Prompt pro další relaci:

> Použij $edupage-development a projektového agenta z AGENTS.md. Přečti docs/AGENT_CONTEXT.md a pokračuj na této změně: [konkrétní požadavek]. Zůstaň na localhostu a nespouštěj testy.

Konfigurace je uložená v projektu podle [AGENTS.md dokumentace](https://learn.chatgpt.com/docs/agent-configuration/agents-md) a [repo-local skills](https://developers.openai.com/blog/skills-agents-sdk). Nejde o další běžící proces nebo vzdáleného agenta.
