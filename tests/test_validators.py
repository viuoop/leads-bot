import pytest

import validators


@pytest.mark.parametrize("raw,want", [
    ("+38 (050) 123-45-67", "+380501234567"),
    ("0501234567", "0501234567"),
    ("123", None), ("abc", None), ("", None),
])
def test_parse_phone(raw, want):
    assert validators.parse_phone(raw) == want


def test_check_text():
    assert validators.check_text("  Иван ") == "Иван"
    assert validators.check_text("   ") is None
    assert validators.check_text(None) is None
    assert validators.check_text("x" * 1001) is None
    assert validators.check_text("x" * 1000) == "x" * 1000
