import json
import sqlite3
from datetime import datetime, timedelta, timezone

_path = ""


def init(path: str) -> None:
    global _path
    _path = path
    with sqlite3.connect(_path) as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS leads(id INTEGER PRIMARY KEY, created_at TEXT, "
            "user_id INTEGER, username TEXT, answers TEXT)"
        )


def add_lead(user_id, username, answers, now=None) -> int:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    with sqlite3.connect(_path) as c:
        cur = c.execute(
            "INSERT INTO leads(created_at, user_id, username, answers) VALUES(?,?,?,?)",
            (now.isoformat(), user_id, username, json.dumps(answers, ensure_ascii=False)),
        )
        return cur.lastrowid


def _where(user_id) -> tuple[str, tuple]:
    return ("user_id = ?", (user_id,)) if user_id is not None else ("1", ())


def all_leads(user_id=None) -> list[dict]:
    cond, args = _where(user_id)
    with sqlite3.connect(_path) as c:
        rows = c.execute(
            f"SELECT id, created_at, user_id, username, answers FROM leads WHERE {cond} ORDER BY id", args
        ).fetchall()
    return [
        {"id": i, "created_at": t, "user_id": u, "username": n, "answers": json.loads(a)}
        for i, t, u, n, a in rows
    ]


def stats(now=None, user_id=None) -> dict[str, int]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    cond, args = _where(user_id)
    # shortcut: created_at compared as ISO text, valid because all rows are stored in UTC
    with sqlite3.connect(_path) as c:
        q = f"SELECT COUNT(*) FROM leads WHERE {cond} AND created_at >= ?"
        today = c.execute(q, (*args, midnight.isoformat())).fetchone()[0]
        week = c.execute(q, (*args, (now - timedelta(days=7)).isoformat())).fetchone()[0]
        total = c.execute(f"SELECT COUNT(*) FROM leads WHERE {cond}", args).fetchone()[0]
    return {"today": today, "week": week, "total": total}
