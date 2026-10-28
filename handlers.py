import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import admin
import db
from config import DEMO_MODE, STEPS, TEXTS
from validators import check_text, parse_phone

router = Router()


class Form(StatesGroup):
    step = State()


def _kb(*buttons: tuple[str, str]):
    b = InlineKeyboardBuilder()
    for text, data in buttons:
        b.button(text=text, callback_data=data)
    b.adjust(1)
    return b.as_markup()


async def ask(message: Message, i: int, remove_kb: bool = False) -> None:
    step = STEPS[i]
    if step["type"] == "phone":
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=TEXTS["share_contact"], request_contact=True)]],
            resize_keyboard=True, one_time_keyboard=True,
        )
        await message.answer(step["prompt"], reply_markup=kb)
    elif step["type"] == "choice":
        kb = _kb(*((o, f"lead:opt:{i}:{n}") for n, o in enumerate(step["options"])))
        await message.answer(step["prompt"], reply_markup=kb)
    else:
        await message.answer(step["prompt"], reply_markup=ReplyKeyboardRemove() if remove_kb else None)


async def advance(message: Message, state: FSMContext, i: int, answers: dict, remove_kb: bool = False) -> None:
    i += 1
    await state.update_data(i=i, answers=answers)
    if i < len(STEPS):
        await ask(message, i, remove_kb)
        return
    lines = "\n".join(f"{s['title']}: {answers[s['key']]}" for s in STEPS)
    kb = _kb((TEXTS["send_button"], "lead:send"), (TEXTS["restart_button"], "lead:restart"))
    await message.answer(f"{TEXTS['confirm']}\n\n{lines}", reply_markup=kb)  # no parse_mode: raw text is safe


async def begin(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.step)
    await state.set_data({"i": 0, "answers": {}})
    await ask(message, 0)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS["demo_start" if DEMO_MODE else "start"], reply_markup=_kb((TEXTS["start_button"], "lead:start")))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TEXTS["cancelled"], reply_markup=ReplyKeyboardRemove())


@router.callback_query(F.data == "lead:start")
async def cb_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await begin(callback.message, state)


@router.callback_query(F.data == "lead:restart", Form.step)
async def cb_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await begin(callback.message, state)


@router.callback_query(F.data == "lead:send", Form.step)
async def cb_send(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    answers = data.get("answers", {})
    if data.get("i") != len(STEPS) or len(answers) != len(STEPS):
        await callback.answer()
        return
    await state.clear()  # before saving: a double tap finds no state
    user = callback.from_user
    try:
        lead_id = db.add_lead(user.id, user.username, answers)
    except Exception:
        logging.exception("add_lead failed")
        await state.set_state(Form.step)
        await state.set_data(data)
        await callback.answer(TEXTS["save_error"], show_alert=True)
        return
    await callback.answer()
    await admin.notify_admins(callback.bot, lead_id, user, answers)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(TEXTS["thanks"], reply_markup=ReplyKeyboardRemove())


@router.callback_query(F.data.startswith("lead:opt:"), Form.step)
async def cb_option(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    i = data.get("i", len(STEPS))
    step_idx, _, idx = callback.data.removeprefix("lead:opt:").partition(":")
    if i >= len(STEPS) or STEPS[i]["type"] != "choice" or step_idx != str(i) \
            or not idx.isdigit() or int(idx) >= len(STEPS[i]["options"]):
        await callback.answer()
        return
    await callback.answer()
    answers = {**data["answers"], STEPS[i]["key"]: STEPS[i]["options"][int(idx)]}
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await advance(callback.message, state, i, answers)


@router.callback_query(F.data.startswith("lead:"))
async def cb_stale(callback: CallbackQuery) -> None:
    await callback.answer()


@router.message(Form.step)
async def on_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    i = data.get("i", len(STEPS))
    if i >= len(STEPS):
        return  # waiting for send/restart buttons
    step = STEPS[i]
    value = None
    if step["type"] == "phone":
        value = message.contact.phone_number if message.contact else parse_phone(message.text or "")
    elif step["type"] == "text":
        value = check_text(message.text)
    if value is None:
        await message.answer(TEXTS["bad_input"])
        await ask(message, i)
        return
    # inline markup can't be combined with ReplyKeyboardRemove; the phone keyboard is one_time, so Telegram hides it anyway
    await advance(message, state, i, {**data["answers"], step["key"]: value}, step["type"] == "phone")
