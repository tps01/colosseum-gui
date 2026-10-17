"""Shared backend protocols for web and desktop GUI drivers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pathlib import Path


class WebBackend(Protocol):
    """Surface used by ``col.gui.web`` (Playwright / sim)."""

    driver_name: str

    def close(self) -> None: ...

    def navigate(self, *, url: str) -> None: ...

    def click(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
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
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
        input: str | None = None,
    ) -> None: ...

    def select_option(
        self,
        *,
        value: str | None = None,
        label: str | None = None,
        index: int | None = None,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
    ) -> None: ...

    def press_key(self, *, key: str) -> None: ...

    def hover(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> None: ...

    def wait(
        self,
        *,
        until: str,
        timeout_s: float = 10.0,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
        text: str | None = None,
    ) -> None: ...

    def wait_stable(self, *, timeout_s: float = 2.0) -> None: ...

    def capture_screenshot(self, *, path: Path) -> Path: ...

    def capture_tree(self) -> object: ...

    def capture_meta(self) -> dict[str, Any]: ...

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> str: ...

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> bool: ...

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> bool: ...

    def measure_navigation_ms(self) -> float: ...


class DesktopBackend(Protocol):
    """Surface used by ``col.gui.desktop`` (FlaUI / sim / generic).

    UIA methods (``get_text``, ``is_visible``, ``is_enabled``, tree ``wait``) are
    implemented by FlaUI and desktop sim; ``driver=generic`` raises
    :class:`~colosseum_gui.exceptions.GuiCapabilityError` via ``unsupported()``.
    """

    driver_name: str

    def close(self) -> None: ...

    def click(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
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
        automation_id: str | None = None,
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
        automation_id: str | None = None,
        xpath: str | None = None,
        image: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> None: ...

    def wait(
        self,
        *,
        until: str,
        timeout_s: float = 10.0,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        text: str | None = None,
        xpath: str | None = None,
    ) -> None: ...

    def wait_stable(self, *, timeout_s: float = 2.0) -> None: ...

    def capture_screenshot(self, *, path: Path) -> Path: ...

    def capture_tree(self) -> object: ...

    def capture_meta(self) -> dict[str, Any]: ...

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> str: ...

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool: ...

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool: ...
