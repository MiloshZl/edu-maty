"""Only this module knows the third-party library. No messages or write calls."""
from datetime import date, datetime, timedelta
from .calculations import PRAGUE, weighted_average
from .models import Result

def timestamp():
    return datetime.now(PRAGUE).isoformat()

def safe_error(exc):
    name = type(exc).__name__
    return {
        "BadCredentialsException": "Přihlášení bylo odmítnuto nebo chybí přihlašovací token.",
        "CaptchaException": "EduPage požaduje CAPTCHA. Dokončete přihlášení na webu školy; prototyp CAPTCHA nepodporuje.",
        "InsufficientPermissionsException": "Účet nemá potřebné oprávnění.",
        "ExpiredSessionException": "Relace EduPage vypršela. Přihlaste se znovu.",
        "NotLoggedInException": "Relace EduPage není přihlášená.",
        "MissingDataException": "Zdroj neposkytl potřebná data; nejde o ověřený prázdný výsledek.",
        "FailedToParseGradeDataError": "Změněný nebo neúplný formát známek.",
        "PermissionError": "EduPage požaduje druhý faktor. Dokončení 2FA tento prototyp zatím nepodporuje.",
    }.get(name, "Načtení selhalo: síťová chyba nebo neúplný či změněný formát zdroje.")

def normalize_lesson(l, day, index):
    # Required fields fail closed on schema changes; unknown optional values stay null.
    subject = l.subject
    return {"id": f"{day}:{l.period}:{index}", "date": str(day), "period": l.period,
            "start": l.start_time.isoformat() if l.start_time else None,
            "end": l.end_time.isoformat() if l.end_time else None, "duration": l.duration,
            "subjectId": str(subject.subject_id) if subject else None,
            "subject": subject.name if subject else None,
            "teachers": [t.name for t in l.teachers] if l.teachers is not None else None,
            "rooms": [r.name for r in l.classrooms] if l.classrooms is not None else None,
            "groups": l.groups, "change": "cancelled" if l.is_cancelled else "unknown",
            "changeSource": "source" if l.is_cancelled else None, "original": None,
            "isEvent": l.is_event}

def normalize_grade(g, index):
    kind = "numeric" if not g.verbal and g.max_points is None and g.percent is None and isinstance(g.grade_n, (int,float)) and 1 <= g.grade_n <= 5 else "other"
    return {"id": f"{g.subject_id}:{g.event_id}:{index}", "subjectId": str(g.subject_id),
            "subject": g.subject_name, "value": g.grade_n, "weight": g.importance,
            "date": g.date.isoformat(), "title": g.title, "comment": g.comment,
            "kind": kind, "included": None, "maxPoints": g.max_points,
            "limitation": "Knihovna nevrací spolehlivý příznak započítání ani pravidla kategorií. Živý průměr nelze věrně reprodukovat."}

class Adapter:
    def __init__(self, mode="live"):
        self.mode = mode
        self.client = None

    def login(self, username, password):
        if self.mode == "demo":
            return
        from edupage_api import Edupage
        self.client = Edupage(request_timeout=12)
        try:
            second_factor = self.client.login(username, password, "spszl")
            if second_factor is not None:
                raise PermissionError("2fa")
            if not self.client.is_logged_in:
                raise ValueError("not logged in")
        except Exception:
            self.close()
            raise

    def close(self):
        if self.client:
            self.client.session.cookies.clear()
            self.client.session.close()
            self.client.data = None
            self.client = None

    def result(self, status, period, data=None, reason=None, limitations=None):
        now = timestamp()
        return Result(status=status, source=self.mode, period=period, data=data, reason=reason,
                      limitations=limitations or [], lastAttempt=now,
                      lastSuccess=now if status in ("ok", "partial") and data is not None else None,
                      liveVerified=self.mode == "live" and status in ("ok", "partial") and data is not None)

    def timetable(self, start, end):
        period = {"from": str(start), "to": str(end), "type": "daily"}
        lessons, failures, verified_days = [], [], []
        for n in range((end-start).days+1):
            day = start+timedelta(days=n)
            try:
                if self.mode == "demo":
                    rows = demo_lessons(day)
                else:
                    table = self.client.get_my_timetable(day)
                    if table is None:
                        raise ValueError("missing timetable")
                    rows = [normalize_lesson(l, day, i) for i,l in enumerate(table.lessons)]
                lessons.extend(rows)
                verified_days.append(str(day))
            except Exception as exc:
                failures.append({"date": str(day), "reason": safe_error(exc)})
        status = "partial" if failures and verified_days else "error" if failures else "ok"
        return self.result(status, period, {"lessons": lessons, "verifiedDays": verified_days, "failedDays": failures} if verified_days else None,
                           reason="Některé dny se nepodařilo načíst." if failures else None,
                           limitations=["Pouze výsledný osobní denní rozvrh. Stálý rozvrh a původní hodnoty nejsou dostupné; kromě zrušení změny nelze potvrdit."])

    def grades(self, year, term):
        period = {"schoolYear": year, "term": term}
        try:
            if self.mode == "demo":
                rows = demo_grades()
            else:
                from edupage_api.grades import Term
                rows = [normalize_grade(g,i) for i,g in enumerate(self.client.get_grades_for_term(year, Term.FIRST if term == 1 else Term.SECOND))]
            subjects = []
            for sid in dict.fromkeys(g["subjectId"] for g in rows):
                gs = [g for g in rows if g["subjectId"] == sid]
                subjects.append({"id":sid, "name":gs[0]["subject"], "grades":gs, "average": weighted_average(gs), "sourceAverage": None})
            return self.result("ok" if self.mode == "demo" or not rows else "partial", period, subjects,
                               limitations=[] if self.mode == "demo" else ["Započítání a kategorie nejsou ověřené; vlastní průměr není dostupný. Slovní pochvaly z oddělené metody nejsou součástí výpisu."])
        except Exception as exc:
            return self.result("error", period, reason=safe_error(exc))

    def attendance(self, year, term):
        p = {"schoolYear":year,"term":term}
        if self.mode == "live":
            return self.result("unsupported",p,reason="Knihovna nemá metodu pro souhrn absence ani uskutečněné hodiny. Vlastní endpoint bez ověření studentského klienta není implementován.")
        return self.result("partial",p,{"excused":8,"unexcused":0,"total":8,"percentage":None,
                                      "subjects":[{"name":"Matematika","missed":3,"taught":None,"percentage":None}]},
                           reason="Procento nelze z dostupných dat spolehlivě určit. Demo obsahuje pouze syntetické počty.")

    def substitutions(self, start, end):
        return self.result("unsupported", {"from":str(start),"to":str(end)},
                           reason="Osobní původní a nové hodnoty nejsou spolehlivě propojené. Zrušené hodiny jsou ve výsledném denním rozvrhu. Školní seznam změn se nenačítá.")

def demo_lessons(day):
    if day.weekday() >= 5:
        return []
    result = []
    for i,(name,start,end) in enumerate([("Matematika","08:00:00","08:45:00"),("Programování","08:55:00","10:30:00"),("Angličtina","10:45:00","11:30:00")]):
        result.append({"id":f"demo:{day}:{i}","date":str(day),"period":i+1,"start":start,"end":end,
                       "duration":2 if i == 1 else 1,"subjectId":str(i),"subject":name,
                       "teachers":["Demo učitel"],"rooms":["Učebna D"],"groups":["Demo skupina A"],
                       "change":"cancelled" if day.weekday()==2 and i==2 else "unchanged",
                       "changeSource":"source","original":None,"isEvent":False})
    return result

def demo_grades():
    return [{"id":f"demo:{i}","subjectId":"0","subject":"Matematika","value":v,"weight":w,
             "date":"2026-10-01","title":title,"comment":None,"kind":kind,"included":True,"maxPoints":None}
            for i,(v,w,title,kind) in enumerate([(1,1,"Opakování", "numeric"),(3,2,"Písemná práce","numeric"),("85 %",None,"Bodové hodnocení","other")])]
