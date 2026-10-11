from datetime import datetime, timezone
import pytest
from app.calculations import weighted_average, attendance_percentage, lesson_now
from app.edupage_adapter import demo_lessons

def g(value=1, weight=1, kind="numeric", included=True):
    return dict(value=value, weight=weight, kind=kind, included=included)

def test_weighted_simulation_and_exclusions():
    assert weighted_average([g(1),g(3,2)])["value"] == pytest.approx(7/3)
    assert weighted_average([g(1),g(3,2),g(1,3)])["value"] == pytest.approx(10/6)
    r=weighted_average([g(1),g(2,None),g(3,-1),g("1-"),g(85,1,"percent"),g(2,1,included=False),g(2,1,included=None),g(2,float('nan'))])
    assert r == {"value":1,"excluded":7,"complete":False}
    assert weighted_average([])["value"] is None

def test_attendance_ratios_and_periods():
    assert attendance_percentage([dict(missed=1,taught=2,period="P1"),dict(missed=1,taught=8,period="P1")]) == 20
    for rows in [[],[dict(missed=0,taught=0,period="P1")],[dict(missed=2,taught=None,period="P1")],[dict(missed=1,taught=2,period="P1"),dict(missed=1,taught=2,period="P2")]]:
        assert attendance_percentage(rows) is None

def test_prague_midnight_dst_double_lesson_and_cancellation():
    from datetime import date
    lessons=demo_lessons(date(2026,10,7))
    now=lesson_now(lessons,datetime(2026,10,7,7,30,tzinfo=timezone.utc))
    assert now["current"]["duration"]==2
    assert now["end"]=="10:30:00" # cancelled last lesson excluded
    assert lesson_now(lessons,datetime(2026,10,6,22,1,tzinfo=timezone.utc))["next"] is not None
    assert lesson_now(lessons,datetime(2026,10,7,22,1,tzinfo=timezone.utc))["next"] is None
    sunday=demo_lessons(date(2026,10,25))
    assert lesson_now(sunday,datetime(2026,10,25,1,30,tzinfo=timezone.utc))["current"] is None
