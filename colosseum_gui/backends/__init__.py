"""Shared backend protocol for web and desktop GUI drivers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class GuiBackend(Protocol):
    """Minimal surface used by ``col.gui.web`` / ``col.gui.desktop`` APIs."""

    driver_name: str

    def close(self) -> None: ...

    def click(
        self,
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
        input: str | None = None,
    ) -> None: ...

    def type_text(
        self,
        *,
        text: str,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        automation_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        image: str | None = None,
        x: float | None = None,
        y: float | None = None,
        input: str | None = None,
    ) -> None: ...

    def press_key(self, *, key: str) -> None: ...

    def hover(
        self,
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
    ) -> None: ...

    def wait_stable(self, *, timeout_s: float = 2.0) -> None: ...

    def capture_screenshot(self, *, path: Path) -> Path: ...

    def capture_meta(self) -> dict[str, Any]: ...
