# Zpráva o napojení EduPage

Datum: 11. 10. 2026. Cílová škola: SPŠ Zlín, `spszl.edupage.org`. **Uživatel potvrdil úspěšné načtení denního rozvrhu.** Ostatní funkce a úplné srovnání dat zůstávají NEOVĚŘENO. Agentovi nebyly poskytnuty a agent nepoužil skutečné přihlašovací údaje.

## Knihovna a zdroje

- Použitá knihovna: **edupage-api 0.13.1**, instalovaná z [PyPI](https://pypi.org/project/edupage-api/0.13.1/).
- Zdrojový projekt: [EdupageAPI/edupage-api](https://github.com/EdupageAPI/edupage-api). Jde o neoficiální knihovnu.
- Licence: GPL-3.0; metadata balíčku deklarují GPLv3+. Licence je dostupná v [repozitáři](https://github.com/EdupageAPI/edupage-api/blob/master/LICENSE). Při případné distribuci je nutné respektovat její podmínky.
- Před implementací byly přečteny zdroje loginu, rozvrhu a známek; následně ověřeny datové třídy a signatury přímo v instalované verzi 0.13.1. Knihovna nebyla upravována. Vlastní normalizace je v `backend/app/edupage_adapter.py`.
- Alternativní projekt loumadev nebyl použit. Vlastní HTTP adaptér absence nebyl implementován: bez přihlášeného studentského klienta chybí ověřená specifikace odpovědí a jejich významu. Endpointy se neodhadují.
- Přímé verze jsou v `backend/requirements.txt`, všechny instalované Python závislosti v `backend/requirements-lock.txt`. Node závislosti uzamyká `frontend/package-lock.json`.

## Dostupnost funkcí

„Automaticky ověřeno“ níže znamená syntetická data a izolované testy provedené **před posledním pokynem uživatele**. Nepotvrzuje živou integraci a nezahrnuje následné dokončovací změny.

| Funkce | Podpora v kódu | Automatické ověření před dokončením | Živé ověření SPŠ Zlín |
| --- | --- | --- | --- |
| Osobní denní rozvrh | `get_my_timetable(date)`; normalizace hodin a stav jednotlivých dnů | Úspěšná, prázdná, neúplná a změněná syntetická odpověď; skutečné datové třídy knihovny | Načtení potvrzeno uživatelem; přesná shoda hodin zatím neověřena |
| Osobní skupiny | Pole `Lesson.groups`; nepoužívají se ID cizích studentů | Fixture s více skupinami | NEOVĚŘENO |
| Stálý rozvrh | Zatím neimplementovaný; není načítán odděleně od denního výsledku | Nepodporováno | NEOVĚŘENO; nedostupnost na EduPage nebyla prokázána |
| Suplování | Zrušení z `Lesson.is_cancelled`; osobní podrobný seznam změn nepodporován | Zrušená hodina a příznak zdrojového potvrzení | NEOVĚŘENO |
| Známky a váhy | `get_grades_for_term(year, Term)`; běžné známky i jiné hodnoty se zobrazují | Normalizace skutečné datové třídy, body, plus/minus a chybějící započítání | NEOVĚŘENO |
| Vlastní vážený průměr a simulace | Jen pro numeric 1–5, kladnou známou váhu a prokázané započítání; živé započítání není dostupné | Výpočty, hypotetické známky, vyloučení neplatných vah a typů | NEOVĚŘENO |
| Celková absence | LIVE `unsupported`; DEMO syntetické počty | Nedostupnost odlišena od nuly | NEOVĚŘENO |
| Absence po předmětech | LIVE `unsupported`; DEMO pouze syntetický příklad | Poměr součtů, nesoulad období a neznámý jmenovatel | NEOVĚŘENO |
| Skutečně uskutečněné hodiny | Nedostupné, neopakujeme týdenní rozvrh do historie | Null pro neznámý/nulový jmenovatel | NEOVĚŘENO |

## Doložená omezení

1. **Rozvrh:** knihovna vrací výsledný plán dne, datum dodává náš dotaz. Původní učitel, učebna a předmět nejsou v datové třídě `Lesson`. Změny se proto neodvozují ani nevydávají za potvrzené suplování. Nezrušené živé hodiny mají stav změny `unknown`.
2. **Klíč hodiny:** knihovna neposkytuje stabilní ID. Používá se složený klíč `datum:pořadí:pozice ve výsledném seznamu`; je stabilní pro nezměněnou odpověď, ale při změně pořadí položek se může změnit. Není vhodný pro dlouhodobé sledování změn bez dalšího zdrojového klíče.
3. **Význam vah:** parser běžných známek používá `importance = p_vaha / 20`. U bodového hodnocení bere `p_vaha` jako maximální počet bodů a `importance` je null. Náš výpočet nepřevádí body/procenta na stupnici 1–5 a nenahrazuje chybějící váhy jedničkou.
4. **Započítání a kategorie:** `EduGrade` neposkytuje spolehlivý příznak započítání ani úplná pravidla kategorií. Živé položky mají `included=null`. Zobrazují se, ale vlastní průměr je neznámý. Simulovaný výsledek při těchto omezeních zahrnuje pouze podporované známé položky a je označený jako neúplný. `class_grade_avg` je průměr třídy, nikoli osobní průměr studenta; není zobrazován jako jeho zdrojový průměr.
5. **Slovní hodnocení:** nenumerické hodnoty vrácené metodou známek se zobrazují. Oddělený výpis pochval `get_text_grades_for_term` není načítán.
6. **Absence:** veřejné metody instalované knihovny nemají potřebný souhrn absence ani historický počet skutečně uskutečněných započítaných hodin. Rozvrh nepoužíváme jako přesný jmenovatel. Skupiny, školní akce a pozdní příchody bez takového podkladu nelze spolehlivě interpretovat.
7. **Půlnoc:** časové pásmo a lokální datum jsou Europe/Prague. Knihovní parser ovšem nahrazuje zdrojový čas `24:00` hodnotou `23:59`; adaptér nemá původní text, takže tuto ztrátu přesnosti neumí napravit. Běžné školní hodiny nejsou přes půlnoc; přeshraniční hodiny nejsou podporovaným scénářem MVP.
8. **CAPTCHA / 2FA:** knihovna rozlišuje CAPTCHA a vrací objekt druhého faktoru. Prototyp tyto stavy bezpečně odmítne, zavře session a zobrazí vysvětlení. Dokončení druhého faktoru ani import webových cookies není implementován.
9. **Chyby:** výjimky knihovny pro oprávnění, chybějící data, parsování a vypršení relace se převádí na stručné zprávy. Obecnou síťovou chybu a neznámou změnu formátu nemusí být možné odlišit; klient proto dostává společnou bezpečnou příčinu bez tracebacku. U neúplného týdne jsou úspěšné a nedostupné dny oddělené.
10. **Cache:** GET endpointy pouze čtou paměťovou cache. Přihlášení a ruční obnovení synchronizují data. Neúspěšné obnovení zachová předchozí data a jejich čas úspěchu, ale označí je jako zastaralá. Prázdný úspěšný seznam se odlišuje od `data=null`.

`liveVerified=true` v odpovědi znamená úspěšné skutečné načtení dané funkce v aktuální relaci. Neznamená, že byl každý údaj ručně porovnán se školním webem. Uživatel potvrdil načtení denního rozvrhu; úplné srovnání údajů zatím nebylo doloženo.

## Kontroly a konečný stav

Před přerušením prošlo **11 backendových testů**, **3 frontendové testy**, TypeScript kontrola a produkční build s Vite 6.3.5. Kontrola npm nalezla zranitelnosti této verze a Vite bylo aktualizováno na **8.3.4**; instalace oznámila nula zranitelností. Build ani testy po aktualizaci a posledních úpravách relací **nebyly znovu spuštěny na výslovné přání uživatele**. Případný starší adresář `frontend/dist` není ověřený výstup konečného stavu; ke spuštění použijte `npm run dev`.

Backend byl lokálně spuštěn na `127.0.0.1:8000` a poté zastaven. Ovladatelný prohlížeč nebyl dostupný, takže demo průchod UI nebyl ověřen. Nikdy se nepoužívaly skutečné účty, známky, docházka ani HAR.

## Manuální checklist pro uživatele

- [ ] Spustit oba servery podle README a prohlédnout výslovně označený DEMO režim.
- [ ] Odhlásit demo a přihlásit vlastní studentský účet přes lokální formulář.
- [ ] Porovnat konkrétní den rozvrhu se školním webem, včetně vlastní dělené skupiny a dvojhodiny.
- [ ] Porovnat den se zrušenou hodinou nebo suplováním; zaznamenat chybějící detaily, neinterpretovat `unknown` jako nezměněnou hodinu.
- [ ] Porovnat předmět s různými vahami známek ve stejném školním roce a pololetí. Ověřit zvlášť započítávání, bodové hodnocení a kategorie.
- [ ] Porovnat absenci za stejné období na EduPage; dokud není ověřený souhrn i jmenovatel, nepovažovat prototyp za zdroj procentní absence.
- [ ] Zkontrolovat odhlášení a zánik relace po restartu backendu.

## Doporučený další krok

Nejprve provést lokální přihlášení a ruční srovnání osobního rozvrhu a známek. Pokud selže parser, opravit izolovaný adaptér podle skutečné oprávněné odpovědi. Pokud knihovna neposkytuje absenci, až poté prověřit minimální read-only adaptér studentského klienta bez zpráv a bez dat ostatních studentů. O konečné architektuře, hostingu nebo Android widgetu zatím není rozhodnuto.
