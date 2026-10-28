import re


def parse_phone(text: str) -> str | None:
    cleaned = re.sub(r"[\s()\-]", "", text)
    return cleaned if re.fullmatch(r"\+?\d{10,15}", cleaned) else None


def check_text(text: str | None) -> str | None:
    if text is None:
        return None
    text = text.strip()
    return text if 1 <= len(text) <= 1000 else None
