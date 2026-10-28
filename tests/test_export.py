from io import BytesIO

import openpyxl

import export

STEPS = [{"key": "name", "title": "Имя"}, {"key": "city", "title": "Город"}]


def _rows(data):
    return list(openpyxl.load_workbook(BytesIO(data)).active.iter_rows(values_only=True))


def test_xlsx_headers_and_rows():
    lead = {"id": 1, "created_at": "2026-01-01", "user_id": 5, "username": "u",
            "answers": {"name": "Иван", "city": "Самара"}}
    rows = _rows(export.leads_to_xlsx([lead], STEPS))
    assert rows[0] == ("ID", "Дата", "User ID", "Username", "Имя", "Город")
    assert rows[1] == (1, "2026-01-01", 5, "u", "Иван", "Самара")


def test_missing_answer_is_blank():
    lead = {"id": 1, "created_at": "d", "user_id": 5, "username": None, "answers": {"name": "Иван"}}
    assert _rows(export.leads_to_xlsx([lead], STEPS))[1][5] is None


def test_export_empty():
    assert len(_rows(export.leads_to_xlsx([], STEPS))) == 1


def test_formula_like_values_are_text():
    lead = {"id": 1, "created_at": "d", "user_id": 5, "username": "=evil()",
            "answers": {"name": "=1+1", "city": "Самара"}}
    ws = openpyxl.load_workbook(BytesIO(export.leads_to_xlsx([lead], STEPS))).active
    for c in (ws["D2"], ws["E2"]):
        assert c.data_type == "s" and c.value.startswith("'")
    assert ws["F2"].value == "Самара"
