"""Playwright sync driver must be stopped before another one starts."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


class _Page:
    def set_default_timeout(self, timeout: int) -> None:
        _ = timeout


class _Context:
    def new_page(self) -> _Page:
        return _Page()

    def close(self) -> None:
        return


class _Browser:
    def new_context(self, **kwargs: object) -> _Context:
        _ = kwargs
        return _Context()

    def close(self) -> None:
        return


class _Launcher:
    def launch(self, *, headless: bool) -> _Browser:
        _ = headless
        return _Browser()


class _SyncPlaywright:
    """Fail the second start until stop() clears the running loop."""

    running = False
    stops = 0

    def __init__(self) -> None:
        if type(self).running:
            raise RuntimeError(
                "It looks like you are using Playwright Sync API inside the asyncio loop.",
            )
        type(self).running = True
        self.chromium = _Launcher()

    def stop(self) -> None:
        type(self).running = False
        type(self).stops += 1


class _Starter:
    def start(self) -> _SyncPlaywright:
        return _SyncPlaywright()


def test_two_playwright_backends_in_one_process(monkeypatch: pytest.MonkeyPatch) -> None:
    import playwright.sync_api as sync_api
    from colosseum_gui.backends.web.playwright_driver import PlaywrightWebBackend

    _SyncPlaywright.running = False
    _SyncPlaywright.stops = 0
    monkeypatch.setattr(sync_api, "sync_playwright", lambda: _Starter())
    config = {
        "timeout_s": 1,
        "headed": False,
        "browser": "chromium",
        "url": "about:blank",
    }

    first = PlaywrightWebBackend(web_id=1, config=config)
    first.close()
    second = PlaywrightWebBackend(web_id=2, config=config)
    second.close()

    assert _SyncPlaywright.stops == 2
    assert _SyncPlaywright.running is False
