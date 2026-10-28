import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("BOT_TOKEN", "123:abc")

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

import admin
import db
import handlers
from config import STEPS, TEXTS

ANSWERS = {s["key"]: "x" for s in STEPS}
DATA = {"i": len(STEPS), "answers": ANSWERS}


def run_send(monkeypatch, add_lead):
    monkeypatch.setattr(db, "add_lead", add_lead)
    monkeypatch.setattr(admin, "notify_admins", AsyncMock())

    async def go():
        state = FSMContext(MemoryStorage(), StorageKey(1, 1, 1))
        await state.set_state(handlers.Form.step)
        await state.set_data(DATA)
        cb = SimpleNamespace(
            answer=AsyncMock(), bot=None, from_user=SimpleNamespace(id=1, username="u"),
            message=SimpleNamespace(edit_reply_markup=AsyncMock(), answer=AsyncMock()),
        )
        await handlers.cb_send(cb, state)
        return cb, await state.get_state(), await state.get_data()

    return asyncio.run(go())


def test_send_failure_restores_state(monkeypatch):
    def boom(*a):
        raise RuntimeError("db down")

    cb, st, data = run_send(monkeypatch, boom)
    assert st == handlers.Form.step.state
    assert data == DATA
    cb.answer.assert_awaited_once_with(TEXTS["save_error"], show_alert=True)
    cb.message.answer.assert_not_awaited()


def test_send_success_clears_state(monkeypatch):
    calls = []
    cb, st, data = run_send(monkeypatch, lambda *a: calls.append(a) or 7)
    assert st is None and data == {}
    assert len(calls) == 1
    cb.answer.assert_awaited_once_with()
    cb.message.answer.assert_awaited_once()
