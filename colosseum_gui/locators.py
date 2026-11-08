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


def describe_target(
    *,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    automation_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> str:
    """Return the locator label an operator would recognize."""
    if name:
        if role:
            return f"{role} {name}"
        return str(name)
    for value in (test_id, automation_id, css, xpath, image):
        if value:
            return str(value)
    if x is not None and y is not None:
        return f"({x}, {y})"
    if role:
        return str(role)
    return "target"
