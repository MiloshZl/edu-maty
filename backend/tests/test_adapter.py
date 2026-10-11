from datetime import date, time, datetime
from types import SimpleNamespace as NS
from edupage_api.timetables import Lesson, Timetable
from edupage_api.subjects import Subject
from edupage_api.classrooms import Classroom
from edupage_api.grades import EduGrade
from app.edupage_adapter import Adapter, normalize_grade

DAY=date(2026,10,7)

def lesson():
    return Lesson(2,time(8,55),time(10,30),2,Subject(7,"Demo","D"),None,["A","B"],[NS(name="Demo učitel")],[Classroom(1,"D1","D1")],None,None,True,False)

def test_real_library_dataclasses_cancelled_and_groups():
    a=Adapter();a.client=NS(get_my_timetable=lambda d:Timetable([lesson()]))
    r=a.timetable(DAY,DAY)
    assert r.status=="ok"
    l=r.data["lessons"][0]
    assert l["groups"]==["A","B"] and l["change"]=="cancelled"
    assert l["changeSource"]=="source" and l["original"] is None
    assert l["teachers"]==["Demo učitel"]

def test_empty_missing_changed_and_partial():
    a=Adapter();a.client=NS(get_my_timetable=lambda d:Timetable([]))
    assert a.timetable(DAY,DAY).data["lessons"]==[]
    a.client.get_my_timetable=lambda d:None
    assert a.timetable(DAY,DAY).data is None
    a.client.get_my_timetable=lambda d:NS(renamed_lessons=[])
    assert a.timetable(DAY,DAY).status=="error"
    a.client.get_my_timetable=lambda d:Timetable([]) if d==DAY else None
    r=a.timetable(DAY,date(2026,10,8))
    assert r.status=="partial" and r.data["verifiedDays"]==[str(DAY)]

def test_grade_weight_unknown_inclusion_points_and_plus_minus():
    g=EduGrade(1,"Syntetická práce",2,None,datetime(2026,10,1),7,"Demo",None,None,None,1.5,False,None,None)
    normalized=normalize_grade(g,0)
    assert normalized["weight"]==1.5 and normalized["included"] is None
    g.max_points=20
    assert normalize_grade(g,0)["kind"]=="other"
    g.max_points=None;g.grade_n="1-"
    assert normalize_grade(g,0)["kind"]=="other"

def test_live_unsupported_is_not_empty_success():
    a=Adapter()
    assert a.attendance(2026,1).data is None
    assert a.substitutions(DAY,DAY).status=="unsupported"
    assert a.attendance(2026,1).liveVerified is False
