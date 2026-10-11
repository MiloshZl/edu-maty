import asyncio
import os
import secrets
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .calculations import PRAGUE, lesson_now
from .edupage_adapter import Adapter, safe_error, timestamp
from .models import LoginRequest

@asynccontextmanager
async def lifespan(app):
    async def expire_sessions():
        while True:
            await asyncio.sleep(30)
            for token, session in list(sessions.items()):
                if session.expires <= time.monotonic():
                    await remove_session(token)
    cleanup = asyncio.create_task(expire_sessions())
    try:
        yield
    finally:
        cleanup.cancel()
        try:
            await cleanup
        except asyncio.CancelledError:
            pass
        for token in list(sessions):
            await remove_session(token)

app = FastAPI(title="EduPage localhost", docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
COOKIE = "edupage_local"
TTL = 3600
ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}

@dataclass
class Session:
    adapter: Adapter
    expires: float = field(default_factory=lambda: time.monotonic()+TTL)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    cache: dict = field(default_factory=dict)
    last_sync: float = 0
    last_success: str | None = None
    last_attempt: str | None = None
    school_year: int = 2026

sessions: dict[str, Session] = {}
login_attempts: list[float] = []

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo validation inputs (particularly login passwords).
    return JSONResponse({"detail":"Neplatný formát požadavku nebo období."}, status_code=422)

@app.middleware("http")
async def local_guard(request: Request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"} and request.headers.get("origin") not in ORIGINS:
        return JSONResponse({"detail":"Nepovolený Origin."},status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

async def remove_session(token):
    s = sessions.pop(token, None)
    if s:
        async with s.lock:
            s.cache.clear()
            await asyncio.to_thread(s.adapter.close)

async def get_session(request):
    token = request.cookies.get(COOKIE)
    s = sessions.get(token)
    if not s or s.expires <= time.monotonic():
        if s:
            await remove_session(token)
        raise HTTPException(401,"Relace vypršela nebo nejste přihlášeni.")
    return s

def defaults():
    today = datetime.now(PRAGUE).date()
    start = today - timedelta(days=today.weekday())
    year = today.year if today.month >= 9 else today.year-1
    term = 1 if today.month >= 9 or today.month == 1 else 2
    return start, start+timedelta(days=6), year, term

def period_range(start, end):
    if end < start or (end-start).days > 13:
        raise HTTPException(422,"Rozsah musí být 1 až 14 dní.")

def school_period(year, term):
    if year < 2000 or year > datetime.now(PRAGUE).year or term not in (1,2):
        raise HTTPException(422,"Neplatný školní rok nebo pololetí.")

async def synchronize(s, start, end, year, term):
    if s.lock.locked():
        raise HTTPException(409,"Synchronizace již probíhá.")
    async with s.lock:
        if time.monotonic()-s.last_sync < 10:
            raise HTTPException(429,"Obnovení lze opakovat po 10 sekundách.")
        s.last_sync = time.monotonic()
        s.last_attempt = timestamp()
        calls = [("timetable",(start,end)),("substitutions",(start,end)),("grades",(year,term)),("attendance",(year,term))]
        for name,args in calls:
            try:
                result = await asyncio.to_thread(getattr(s.adapter,name),*args)
            except Exception as exc:
                result = s.adapter.result("error", {"selection": [str(a) for a in args]}, reason=safe_error(exc))
            key = (name,*args)
            previous = s.cache.get(key)
            if result.status == "error" and previous and previous.data is not None:
                result.data = previous.data
                result.lastSuccess = previous.lastSuccess
                result.stale = True
            s.cache[key] = result
        successes = [r.lastSuccess for r in s.cache.values() if r.lastSuccess]
        if successes:
            s.last_success = max(successes)

def status(s):
    return {"authenticated":True,"mode":s.adapter.mode,"lastSuccess":s.last_success,
            "lastAttempt":s.last_attempt,"schoolYear":s.school_year,"expiresIn":max(0,int(s.expires-time.monotonic()))}

@app.get("/api/health")
def health():
    return {"status":"ok","school":"spszl","timezone":"Europe/Prague"}

@app.post("/api/auth/login")
async def login(body: LoginRequest, request: Request, response: Response):
    now = time.monotonic()
    login_attempts[:] = [t for t in login_attempts if now-t < 60]
    if len(login_attempts) >= 5:
        raise HTTPException(429,"Příliš mnoho pokusů. Počkejte jednu minutu.")
    login_attempts.append(now)
    for token,s in list(sessions.items()):
        if s.expires <= now:
            await remove_session(token)
    if len(sessions) >= 8:
        raise HTTPException(429,"Příliš mnoho lokálních relací.")
    adapter = Adapter(body.mode)
    if body.mode == "live" and (not body.username.strip() or not body.password.get_secret_value()):
        raise HTTPException(422,"Vyplňte jméno a heslo.")
    try:
        await asyncio.to_thread(adapter.login,body.username,body.password.get_secret_value())
    except Exception as exc:
        raise HTTPException(401,safe_error(exc)) from None
    finally:
        body.password = type(body.password)("")
    old = request.cookies.get(COOKIE)
    if old:
        await remove_session(old)
    s = Session(adapter)
    start,end,year,term = defaults()
    if body.mode == "live":
        try:
            year = int(await asyncio.to_thread(adapter.client.get_school_year))
        except Exception:
            pass
    s.school_year = year
    token = secrets.token_urlsafe(32)
    sessions[token] = s
    await synchronize(s,start,end,year,term)
    response.set_cookie(COOKIE,token,max_age=TTL,httponly=True,samesite="strict",
                        secure=os.getenv("EDUPAGE_SECURE_COOKIE") == "1",path="/api")
    return status(s)

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    await remove_session(request.cookies.get(COOKIE))
    response.delete_cookie(COOKIE,path="/api")
    return {"authenticated":False}

@app.get("/api/auth/status")
async def auth_status(request: Request):
    try:
        return status(await get_session(request))
    except HTTPException:
        return {"authenticated":False}

@app.post("/api/sync")
async def sync(request: Request, start: date = Query(alias="from"), end: date = Query(alias="to"), schoolYear: int = 2026, term: int = 1):
    period_range(start,end)
    school_period(schoolYear,term)
    s = await get_session(request)
    await synchronize(s,start,end,schoolYear,term)
    return status(s)

async def cached(request, name, args):
    s = await get_session(request)
    value = s.cache.get((name,*args))
    if not value:
        return s.adapter.result("not_verified",{"selection":[str(a) for a in args]},reason="Vybrané období ještě nebylo načteno. Stiskněte Obnovit.")
    value = value.model_copy(deep=True)
    if value.lastSuccess:
        value.stale = value.stale or (datetime.now(PRAGUE)-datetime.fromisoformat(value.lastSuccess)).total_seconds()>300
    return value

@app.get("/api/timetable")
async def timetable(request: Request, start: date = Query(alias="from"), end: date = Query(alias="to")):
    period_range(start,end)
    r = await cached(request,"timetable",(start,end))
    if r.data:
        r.data["now"] = lesson_now(r.data["lessons"],datetime.now(PRAGUE))
    return r

@app.get("/api/substitutions")
async def substitutions(request: Request, start: date = Query(alias="from"), end: date = Query(alias="to")):
    period_range(start,end)
    return await cached(request,"substitutions",(start,end))

@app.get("/api/grades")
async def grades(request: Request, schoolYear: int, term: int):
    school_period(schoolYear,term)
    return await cached(request,"grades",(schoolYear,term))

@app.get("/api/attendance")
async def attendance(request: Request, schoolYear: int, term: int):
    school_period(schoolYear,term)
    return await cached(request,"attendance",(schoolYear,term))

@app.get("/api/capabilities")
async def capabilities(request: Request):
    s = await get_session(request)
    return [{"feature":key[0], **r.model_dump(exclude={"data"})} for key,r in s.cache.items()]
