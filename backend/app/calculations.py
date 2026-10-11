from datetime import datetime
from math import isfinite
from zoneinfo import ZoneInfo

PRAGUE = ZoneInfo("Europe/Prague")

def weighted_average(grades):
    valid = []
    for g in grades:
        value, weight = g.get("value"), g.get("weight")
        if (g.get("kind") == "numeric" and g.get("included") is True
            and isinstance(value, (int, float)) and not isinstance(value, bool)
            and isinstance(weight, (int, float)) and not isinstance(weight, bool)
            and isfinite(value) and isfinite(weight) and 1 <= value <= 5 and weight > 0):
            valid.append((value, weight))
    return {"value": sum(v*w for v,w in valid)/sum(w for _,w in valid) if valid else None,
            "excluded": len(grades)-len(valid), "complete": len(valid) == len(grades)}

def attendance_percentage(rows):
    if not rows or len({r.get("period") for r in rows}) != 1:
        return None
    if any(r.get("missed") is None or r.get("taught") is None
           or r["taught"] <= 0 or r["missed"] < 0 or r["missed"] > r["taught"] for r in rows):
        return None
    return sum(r["missed"] for r in rows)/sum(r["taught"] for r in rows)*100

def lesson_now(lessons, now: datetime):
    local = now.astimezone(PRAGUE)
    today = sorted((l for l in lessons if l["date"] == local.date().isoformat()
                    and l["change"] != "cancelled" and l["start"] and l["end"]), key=lambda l:l["start"])
    clock = local.strftime("%H:%M:%S")
    return {"current": next((l for l in today if l["start"] <= clock < l["end"]), None),
            "next": next((l for l in today if l["start"] > clock), None),
            "end": max((l["end"] for l in today), default=None)}
