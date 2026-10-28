from io import BytesIO

from openpyxl import Workbook


def _safe(v):
    # a leading ' keeps Excel from treating user text as a formula
    return "'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v


def leads_to_xlsx(leads: list[dict], steps: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Дата", "User ID", "Username", *(s["title"] for s in steps)])
    for l in leads:
        ws.append([l["id"], l["created_at"], l["user_id"], _safe(l["username"]),
                   *(_safe(l["answers"].get(s["key"])) for s in steps)])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
