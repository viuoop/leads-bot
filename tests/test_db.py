from datetime import datetime, timezone

import db


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


def test_add_and_list(tmp_path):
    db.init(str(tmp_path / "t.db"))
    a = db.add_lead(1, "ivan", {"name": "Иван"})
    b = db.add_lead(2, "petr", {"name": "Пётр"})
    leads = db.all_leads()
    assert len(leads) == 2
    assert leads[0]["answers"] == {"name": "Иван"}
    assert leads[0]["id"] == a < b == leads[1]["id"]


def test_unicode_and_none_username(tmp_path):
    db.init(str(tmp_path / "t.db"))
    db.add_lead(1, None, {"msg": "Привет 👋"})
    lead = db.all_leads()[0]
    assert lead["username"] is None
    assert lead["answers"] == {"msg": "Привет 👋"}


def test_stats(tmp_path):
    db.init(str(tmp_path / "t.db"))
    for d in [(2026, 10, 28, 1), (2026, 10, 25, 12), (2026, 10, 10, 12)]:
        db.add_lead(1, "u", {}, now=utc(*d))
    assert db.stats(utc(2026, 10, 28, 12)) == {"today": 1, "week": 2, "total": 3}
