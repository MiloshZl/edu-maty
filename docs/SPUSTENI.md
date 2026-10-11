# Lokální spuštění EduPage

Projekt zatím běží pouze na tomto počítači. Python, `.venv` a závislosti jsou v tomto workspace připravené. Otevřete **dva PowerShell terminály**.

## 1. Backend

V prvním terminálu:

```powershell
Set-Location 'C:\Users\krcma\maty-sklep-old\projekty\edupageMatyTest'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

Terminál ponechte otevřený. Backend poslouchá na `http://127.0.0.1:8000`.

## 2. Frontend

Ve druhém terminálu:

```powershell
Set-Location 'C:\Users\krcma\maty-sklep-old\projekty\edupageMatyTest\frontend'
npm.cmd run dev
```

Také tento terminál ponechte otevřený.

## 3. Aplikace

Otevřete **http://127.0.0.1:5173**.

- Pro LIVE zadejte své studentské jméno a heslo do formuláře. Škola je pevně `spszl.edupage.org`. Údaje neposílejte do chatu ani neukládejte do souborů.
- Pro ukázku zvolte **Otevřít DEMO se syntetickými daty**. Demo nepotřebuje přihlášení do EduPage.
- Po přihlášení se načte aktuální týden. Po změně týdne, školního roku nebo pololetí stiskněte **Obnovit**. Obnovení lze opakovat po 10 sekundách.
- Přepnutí záložek neobnovuje data na EduPage.
- Uživatel potvrdil úspěšné načtení denního rozvrhu. **Stálý rozvrh zatím není implementován**; hláška o jeho nedostupnosti neznamená chybu načtení denního rozvrhu.
- Živá absence a podrobné osobní suplování zatím nejsou implementované. Dostupnost jednotlivých funkcí je v diagnostice.

## Vypnutí a restart

V aplikaci můžete použít **Odhlásit**. Poté stiskněte **Ctrl+C v obou terminálech**. Znovu spusťte stejné příkazy, až budete chtít aplikaci otevřít.

Po restartu backendu se přihlaste znovu. Relace má platnost jednu hodinu a spolu s cache zůstává pouze v paměti backendu. Spuštění aplikace **nespouští testy**.

## Nová instalace nebo obnova prostředí

Tyto kroky nejsou potřeba při běžném spuštění. Požadavky: Python 3.12 a Node.js 22.12+ nebo 24+ s npm.

Z kořene projektu:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-lock.txt
Set-Location frontend
npm.cmd ci
```

Pokud nemáte příkaz `py`, pro vytvoření venv zde můžete použít připravený lokální Python:

```powershell
.\.runtime\python\cpython-3.12.12-windows-x86_64-none\python.exe -m venv .venv
```

Venv nemusíte aktivovat ani měnit PowerShell ExecutionPolicy. Po přesunu projektu vytvořte nové venv; původní prostředí není přenositelné. Docker není potřeba.

## Běžné potíže

| Problém | Postup |
| --- | --- |
| Aplikace se neotevře | Ověřte, že oba terminály běží, a použijte přesně `http://127.0.0.1:5173`. |
| Obsazený port 5173 nebo 8000 | Ukončete svůj předchozí server pomocí Ctrl+C. Porty neměňte bez úpravy proxy a povoleného Origin. |
| Období není načtené | Stiskněte Obnovit. „Neověřeno“ neznamená prázdný rozvrh. |
| Relace vypršela | Přihlaste se znovu v aplikaci. |
| CAPTCHA nebo 2FA | Jejich dokončení prototyp zatím nepodporuje. Přihlášení na školním webu nepřenáší relaci do prototypu. |
| PowerShell blokuje `npm` | Použijte `npm.cmd`, jak uvádí příkazy výše. |

Oba servery ponechte na `127.0.0.1`. Frontend používá Vite proxy `/api`; do EduPage nezapisuje známky, docházku ani zprávy.

Další informace: [README](../README.md), [stav integrace](../INTEGRATION_REPORT.md), [kontext agenta](AGENT_CONTEXT.md).
