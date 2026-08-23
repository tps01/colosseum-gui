"""Factory for ``gui.web`` and ``gui.desktop`` backends."""

from __future__ import annotations

from typing import Any

from colosseum_gui.exceptions import GuiConnectionError


def open_backend(kind: str, resource_id: int, config: dict[str, Any]) -> Any:  # noqa: ANN401
    if kind == "web":
        from colosseum_gui.backends.web.factory import open_web_backend

        return open_web_backend(resource_id, config)
    if kind == "desktop":
        from colosseum_gui.backends.desktop.factory import open_desktop_backend

        return open_desktop_backend(resource_id, config)
    raise GuiConnectionError(f"unsupported gui kind `{kind}`")
