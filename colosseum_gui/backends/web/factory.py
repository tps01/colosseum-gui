"""Web backend factory."""

from __future__ import annotations

from typing import Any

from colosseum_gui.exceptions import GuiConnectionError


def open_web_backend(web_id: int, config: dict[str, Any]) -> Any:  # noqa: ANN401
    driver = str(config.get("driver") or "playwright").lower()
    if driver == "sim":
        from colosseum_gui.backends.web.sim import SimWebBackend

        return SimWebBackend(web_id=web_id, config=config)
    if driver == "playwright":
        from colosseum_gui.backends.web.playwright_driver import PlaywrightWebBackend

        return PlaywrightWebBackend(web_id=web_id, config=config)
    raise GuiConnectionError(f"col.gui.web: unsupported driver `{driver}`")
