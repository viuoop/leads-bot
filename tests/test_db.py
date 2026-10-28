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


def test_filter_by_user(tmp_path):
    db.init(str(tmp_path / "t.db"))
    db.add_lead(1, "a", {"n": "1"}, now=utc(2026, 10, 28, 1))
    db.add_lead(2, "b", {"n": "2"}, now=utc(2026, 10, 28, 2))
    db.add_lead(1, "a", {"n": "3"}, now=utc(2026, 10, 10, 1))
    assert [l["answers"]["n"] for l in db.all_leads(user_id=1)] == ["1", "3"]
    assert db.stats(utc(2026, 10, 28, 12), user_id=1) == {"today": 1, "week": 1, "total": 2}
    assert db.stats(utc(2026, 10, 28, 12), user_id=3) == {"today": 0, "week": 0, "total": 0}
