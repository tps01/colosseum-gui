"""Kind-honest locator guards for web vs desktop backends."""

from __future__ import annotations


def reject_web_locators(*, css: str | None = None, test_id: str | None = None) -> None:
    """Raise if web-only locators were passed to a desktop backend."""
    if css is not None or test_id is not None:
        raise ValueError("css/test_id are web-only; use col.gui.web")


def reject_desktop_locators(*, automation_id: str | None = None) -> None:
    """Raise if desktop-only locators were passed to a web backend."""
    if automation_id is not None:
        raise ValueError("automation_id is desktop-only; use col.gui.desktop")
