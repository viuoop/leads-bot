import logging
from datetime import date
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message, User

import config
import db
from export import leads_to_xlsx

router = Router()
if not config.DEMO_MODE:
    router.message.filter(F.from_user.id.in_(config.ADMIN_IDS))


def scope(message: Message) -> int | None:
    """None = all leads (admin); otherwise only this user's leads (demo visitor)."""
    return None if message.from_user.id in config.ADMIN_IDS else message.from_user.id


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    leads = db.all_leads(scope(message))
    if not leads:
        await message.answer(config.TEXTS["no_leads"])
        return
    data = leads_to_xlsx(leads, config.STEPS)
    await message.answer_document(BufferedInputFile(data, filename=f"leads_{date.today()}.xlsx"))


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    s = db.stats(user_id=scope(message))
    await message.answer(f"Сегодня: {s['today']}\nЗа неделю: {s['week']}\nВсего: {s['total']}")


async def notify_admins(bot: Bot, lead_id: int, user: User, answers: dict[str, str]) -> None:
    lines = "\n".join(f"{escape(s['title'])}: {escape(answers.get(s['key'], ''))}" for s in config.STEPS)
    client = f'<a href="tg://user?id={user.id}">{escape(user.full_name)}</a>'
    if user.username:
        client += f" @{escape(user.username)}"
    text = f"Заявка #{lead_id}\n\n{lines}\n\nКлиент: {client}"
    targets = [(a, text) for a in config.ADMIN_IDS]
    if config.DEMO_MODE and user.id not in config.ADMIN_IDS:
        targets.append((user.id, f"{escape(config.TEXTS['demo_copy'])}\n\n{text}"))
    for chat_id, body in targets:
        try:
            await bot.send_message(chat_id, body, parse_mode="HTML")
        except Exception:
            logging.exception("Не удалось отправить уведомление %s", chat_id)
