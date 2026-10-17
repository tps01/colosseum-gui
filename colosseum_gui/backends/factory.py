"""Factory for ``gui.web`` and ``gui.desktop`` backends."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from colosseum_gui.exceptions import GuiConnectionError

if TYPE_CHECKING:
    from colosseum_gui.backends import DesktopBackend, WebBackend


def open_backend(
    kind: str,
    resource_id: int,
    config: dict[str, Any],
) -> WebBackend | DesktopBackend:
    if kind == "web":
        from colosseum_gui.backends.web.factory import open_web_backend

        return open_web_backend(resource_id, config)
    if kind == "desktop":
        from colosseum_gui.backends.desktop.factory import open_desktop_backend

        return open_desktop_backend(resource_id, config)
    raise GuiConnectionError(f"unsupported gui kind `{kind}`")
