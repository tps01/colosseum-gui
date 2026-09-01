"""Desktop backend factory."""

from __future__ import annotations

import sys
from typing import Any

from colosseum_gui.exceptions import GuiConnectionError

_GENERIC_ALIASES = frozenset({"generic", "x11", ""})


def open_desktop_backend(desktop_id: int, config: dict[str, Any]) -> Any:  # noqa: ANN401
    driver = str(config.get("driver") or _default_driver()).lower()
    if driver == "sim":
        from colosseum_gui.backends.desktop.sim import SimDesktopBackend

        return SimDesktopBackend(desktop_id=desktop_id, config=config)
    if driver in _GENERIC_ALIASES:
        from colosseum_gui.backends.desktop.generic import GenericDesktopBackend

        return GenericDesktopBackend(desktop_id=desktop_id, config=config)
    if driver == "flaui":
        if not sys.platform.startswith("win"):
            raise OSError("flaui is only available on Windows")
        from colosseum_gui.backends.desktop.flaui_driver import FlaUIDesktopBackend

        return FlaUIDesktopBackend(desktop_id=desktop_id, config=config)
    raise GuiConnectionError(f"col.gui.desktop: unsupported driver `{driver}`")


def _default_driver() -> str:
    return "flaui" if sys.platform.startswith("win") else "generic"
