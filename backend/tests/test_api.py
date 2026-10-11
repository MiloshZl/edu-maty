import pytest
from fastapi.testclient import TestClient
from app import main
from app.edupage_adapter import Adapter

ORIGIN={"Origin":"http://127.0.0.1:5173"}

@pytest.fixture(autouse=True)
def clean():
    main.sessions.clear();main.login_attempts.clear()
    yield
    for s in main.sessions.values():s.adapter.close()
    main.sessions.clear()

def login(client):
    return client.post('/api/auth/login',json={"mode":"demo"},headers=ORIGIN)

def selection():
    start,end,year,term=main.defaults()
    return f"from={start}&to={end}&schoolYear={year}&term={term}"

def test_auth_origin_cookie_logout_and_isolation():
    with TestClient(main.app) as a,TestClient(main.app) as b:
        assert a.get('/api/grades?schoolYear=2026&term=1').status_code==401
        assert a.post('/api/auth/login',json={"mode":"demo"}).status_code==403
        r=login(a);assert r.status_code==200
        cookie=r.headers['set-cookie'];assert 'HttpOnly' in cookie and 'SameSite=strict' in cookie and 'Path=/api' in cookie
        assert b.get('/api/timetable?'+selection()).status_code==401
        assert a.get('/api/timetable?'+selection()).json()['source']=='demo'
        assert a.post('/api/auth/logout',headers=ORIGIN).status_code==200
        assert a.get('/api/timetable?'+selection()).status_code==401
        assert not main.sessions

def test_partial_sync_and_failed_refresh_keeps_last_success(monkeypatch):
    with TestClient(main.app) as c:
        monkeypatch.setattr(Adapter,'attendance',lambda self,y,t:self.result('error',{'schoolYear':y,'term':t},reason='Syntetická chyba'))
        assert login(c).status_code==200
        assert c.get('/api/attendance?'+selection()).json()['data'] is None
        before=c.get('/api/timetable?'+selection()).json()
        assert before['status']=='ok'
        monkeypatch.setattr(Adapter,'timetable',lambda self,a,b:self.result('error',{'from':str(a),'to':str(b)},reason='Syntetická chyba'))
        s=next(iter(main.sessions.values()));s.last_sync=0
        assert c.post('/api/sync?'+selection(),headers=ORIGIN).status_code==200
        after=c.get('/api/timetable?'+selection()).json()
        assert after['stale'] and after['lastSuccess']==before['lastSuccess'] and after['data'] is not None

def test_ranges_throttle_expiry_and_no_secret_echo():
    with TestClient(main.app) as c:
        assert login(c).status_code==200
        assert c.get('/api/timetable?from=2026-01-01&to=2026-02-01').status_code==422
        assert c.post('/api/sync?'+selection(),headers=ORIGIN).status_code==429
        assert c.get('/api/grades?schoolYear=2026&term=3').status_code==422
        r=c.post('/api/auth/login',json={"mode":"invalid","password":"SYNTHETIC_SECRET"},headers=ORIGIN)
        assert r.status_code==422 and 'SYNTHETIC_SECRET' not in r.text
        next(iter(main.sessions.values())).expires=0
        assert c.get('/api/timetable?'+selection()).status_code==401
        assert not main.sessions

def test_sync_lock_and_selected_uncached_period():
    import asyncio
    with TestClient(main.app) as c:
        login(c)
        r=c.get('/api/grades?schoolYear=2025&term=2').json()
        assert r['status']=='not_verified' and r['data'] is None
        s=next(iter(main.sessions.values()))
        asyncio.run(s.lock.acquire())
        try:
            assert c.post('/api/sync?'+selection(),headers=ORIGIN).status_code==409
        finally:s.lock.release()
