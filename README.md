# leads-bot

Telegram-бот для сбора заявок: задаёт клиенту вопросы, сохраняет заявку в SQLite и сразу уведомляет админов. Админам доступны `/export` (Excel со всеми заявками) и `/stats` (сегодня / за неделю / всего).

## Запуск

```
uv sync
```

Создай `.env`:

```
BOT_TOKEN=токен от @BotFather
ADMIN_IDS=123456789,987654321
```

`ADMIN_IDS` — Telegram id админов через запятую (каждый должен хотя бы раз написать боту). Затем:

```
uv run bot.py
```

## Настройка под клиента

Всё в `config.py`:

- `STEPS` — вопросы анкеты (`key`, `title`, `type`: `text` / `phone` / `choice`, `prompt`, для `choice` ещё `options`).
- `TEXTS` — все тексты и подписи кнопок бота.

Тесты: `uv run pytest -v`.
