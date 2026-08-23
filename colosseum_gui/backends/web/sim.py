"""Simulated web backend for CI (no browser)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from colosseum_gui.capabilities import unsupported
from colosseum_gui.visual.pngutil import solid_rgb, write_png


class SimWebBackend:
    """In-memory web surface with canned tree and screenshots."""

    driver_name = "sim"

    def __init__(self, *, web_id: int, config: dict[str, Any]) -> None:
        self.web_id = web_id
        self.config = dict(config)
        self.url = str(config.get("url") or "about:blank")
        self._text_by_role: dict[tuple[str, str], str] = {
            ("button", "Start"): "Start",
            ("status", "Ready"): "Ready",
        }
        self._visible: set[tuple[str, str]] = {("button", "Start"), ("status", "Ready")}
        self._enabled: set[tuple[str, str]] = {("button", "Start"), ("status", "Ready")}
        self._last_nav_ms = 1.0
        self._color = (40, 120, 200)

    def close(self) -> None:
        return None

    def navigate(self, *, url: str) -> None:
        self.url = url
        self._last_nav_ms = 5.0

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
    ) -> None:
        _ = (automation_id, image, x, y, input)
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        if key not in self._visible:
            raise LookupError(f"sim web element not found: {key}")
        if key == ("button", "Start"):
            self._visible.add(("status", "Running"))
            self._text_by_role[("status", "Running")] = "Running"

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
    ) -> None:
        _ = (automation_id, image, x, y, input)
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        self._text_by_role[key] = text
        self._visible.add(key)
        self._enabled.add(key)

    def press_key(self, *, key: str) -> None:
        _ = key

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
    ) -> None:
        self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        _ = (automation_id, image, x, y)

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
    ) -> None:
        _ = timeout_s
        if x is not None or y is not None:
            unsupported(
                self.driver_name,
                "coordinate_locate",
                detail="coordinate DOM locators require driver=playwright",
            )
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        if until == "visible" and key not in self._visible:
            raise TimeoutError(f"sim wait visible timed out for {key}")
        if until == "enabled" and key not in self._enabled:
            raise TimeoutError(f"sim wait enabled timed out for {key}")
        if until == "text" and text is not None and self._text_by_role.get(key) != text:
            raise TimeoutError(f"sim wait text timed out for {key}")

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        _ = timeout_s
        time.sleep(0.01)

    def capture_screenshot(self, *, path: Path) -> Path:
        write_png(path, 64, 48, solid_rgb(64, 48, self._color))
        return path

    def capture_tree(self) -> dict[str, Any]:
        nodes = []
        for role, name in sorted(self._visible):
            nodes.append(
                {
                    "role": role,
                    "name": name,
                    "text": self._text_by_role.get((role, name), ""),
                    "enabled": (role, name) in self._enabled,
                }
            )
        return {"url": self.url, "nodes": nodes}

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
    ) -> str:
        if x is not None or y is not None:
            unsupported(
                self.driver_name,
                "coordinate_locate",
                detail="coordinate DOM locators require driver=playwright",
            )
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        return self._text_by_role.get(key, "")

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
    ) -> bool:
        if x is not None or y is not None:
            unsupported(
                self.driver_name,
                "coordinate_locate",
                detail="coordinate DOM locators require driver=playwright",
            )
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        return key in self._visible

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
    ) -> bool:
        if x is not None or y is not None:
            unsupported(
                self.driver_name,
                "coordinate_locate",
                detail="coordinate DOM locators require driver=playwright",
            )
        key = self._resolve_key(role=role, name=name, test_id=test_id, css=css, xpath=xpath)
        return key in self._enabled

    def measure_navigation_ms(self) -> float:
        return float(self._last_nav_ms)

    def capture_meta(self) -> dict[str, Any]:
        return {
            "driver": self.driver_name,
            "web_id": self.web_id,
            "url": self.url,
            "width": 64,
            "height": 48,
            "dpi_scale": 1.0,
        }

    def _resolve_key(
        self,
        *,
        role: str | None,
        name: str | None,
        test_id: str | None,
        css: str | None,
        xpath: str | None,
    ) -> tuple[str, str]:
        if test_id is not None:
            return ("testid", test_id)
        if css is not None:
            return ("css", css)
        if xpath is not None:
            return ("xpath", xpath)
        if role is None or name is None:
            unsupported(
                self.driver_name,
                "locate",
                detail="provide role+name, test_id, css, or xpath",
            )
        return (role, name)
