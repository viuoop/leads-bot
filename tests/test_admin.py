import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("BOT_TOKEN", "123:abc")

import admin
import config

CLIENT = SimpleNamespace(id=555, full_name="<b>Иван</b>", username=None)


def notify(monkeypatch, demo, admins):
    monkeypatch.setattr(config, "DEMO_MODE", demo)
    monkeypatch.setattr(config, "ADMIN_IDS", admins)
    bot = SimpleNamespace(send_message=AsyncMock())
    asyncio.run(admin.notify_admins(bot, 1, CLIENT, {"name": "Иван"}))
    return {c.args[0]: c.args[1] for c in bot.send_message.await_args_list}


def test_demo_sends_copy_to_client(monkeypatch):
    sent = notify(monkeypatch, True, {1})
    assert set(sent) == {1, 555}
    assert sent[555].startswith(config.TEXTS["demo_copy"])
    assert "&lt;b&gt;Иван&lt;/b&gt;" in sent[555]


def test_no_copy_outside_demo(monkeypatch):
    assert set(notify(monkeypatch, False, {1})) == {1}


def test_no_double_copy_for_admin_client(monkeypatch):
    sent = notify(monkeypatch, True, {555})
    assert list(sent) == [555]
    assert not sent[555].startswith(config.TEXTS["demo_copy"])


def test_scope(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_IDS", {1})
    assert admin.scope(SimpleNamespace(from_user=SimpleNamespace(id=1))) is None
    assert admin.scope(SimpleNamespace(from_user=SimpleNamespace(id=2))) == 2
