import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан в .env")

ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
DB_PATH = "leads.db"

STEPS = [
    {"key": "name", "title": "Имя", "type": "text", "prompt": "Как вас зовут?"},
    {"key": "phone", "title": "Телефон", "type": "phone",
     "prompt": "Ваш телефон? Нажмите кнопку или введите номер."},
    {"key": "service", "title": "Услуга", "type": "choice", "prompt": "Какая услуга нужна?",
     "options": ["Консультация", "Разработка", "Поддержка"]},
    {"key": "comment", "title": "Комментарий", "type": "text", "prompt": "Добавьте комментарий:"},
]

TEXTS = {
    "start": "Здравствуйте! Оставьте заявку — ответим в ближайшее время.",
    "start_button": "Оставить заявку",
    "share_contact": "Поделиться контактом",
    "bad_input": "Не получилось разобрать ответ. Попробуйте ещё раз.",
    "confirm": "Проверьте заявку:",
    "send_button": "Отправить",
    "restart_button": "Заполнить заново",
    "thanks": "Спасибо! Заявка отправлена.",
    "cancelled": "Отменено. Чтобы начать заново, нажмите /start.",
    "save_error": "Не удалось сохранить заявку, попробуйте ещё раз.",
    "no_leads": "Заявок пока нет.",
}
