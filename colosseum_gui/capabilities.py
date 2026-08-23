from __future__ import annotations

from typing import NoReturn

from colosseum_gui.exceptions import GuiCapabilityError


def unsupported(driver: str, operation: str, *, detail: str = "") -> NoReturn:
    """Raise :class:`GuiCapabilityError` for an unsupported driver operation."""
    message = f"{operation} is not supported by driver `{driver}`"
    if detail:
        message = f"{message} ({detail})"
    raise GuiCapabilityError(message)
