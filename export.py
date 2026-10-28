from io import BytesIO

from openpyxl import Workbook


def leads_to_xlsx(leads: list[dict], steps: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Дата", "User ID", "Username", *(s["title"] for s in steps)])
    for l in leads:
        ws.append([l["id"], l["created_at"], l["user_id"], l["username"],
                   *(l["answers"].get(s["key"]) for s in steps)])
        for c in ws[ws.max_row][3:]:  # user-supplied cells: force text so Excel never evaluates them
            if isinstance(c.value, str):
                c.data_type, c.quotePrefix = "s", True
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
