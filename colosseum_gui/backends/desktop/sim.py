"""Simulated desktop backend for CI (no display)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from colosseum_gui.capabilities import unsupported
from colosseum_gui.visual import find_template
from colosseum_gui.visual.pngutil import read_png, solid_rgb, write_png


class SimDesktopBackend:
    """In-memory desktop surface with image/coord clicks and canned UIA tree."""

    driver_name = "sim"

    def __init__(self, *, desktop_id: int, config: dict[str, Any]) -> None:
        self.desktop_id = desktop_id
        self.config = dict(config)
        self.title = str(config.get("title") or "SimWindow")
        self._color = (30, 30, 30)
        self._width = 80
        self._height = 60
        # Painted "button" region for image-match demos.
        self._button_rect = (10, 10, 20, 12)  # x, y, w, h
        self._uia: dict[str, dict[str, Any]] = {
            "StartBtn": {
                "automation_id": "StartBtn",
                "name": "Start",
                "role": "button",
                "text": "Start",
                "visible": True,
                "enabled": True,
            },
        }
        self._last_click: tuple[float, float] | None = None

    def close(self) -> None:
        return None

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
        self._reject_web_locators(css=css, test_id=test_id)
        if automation_id or role or name or xpath:
            node = self._find_uia(
                automation_id=automation_id,
                role=role,
                name=name,
                xpath=xpath,
            )
            _ = input
            if not node.get("enabled"):
                raise RuntimeError(f"sim control not enabled: {node}")
            if node.get("automation_id") == "StartBtn":
                node["text"] = "Running"
            return
        if image is not None:
            self._click_image(image)
            return
        if x is not None and y is not None:
            self._last_click = (float(x), float(y))
            return
        unsupported(
            self.driver_name,
            "click",
            detail="provide automation_id/role+name, image=, or x+y",
        )

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
        self._reject_web_locators(css=css, test_id=test_id)
        _ = (image, x, y, input)
        if automation_id or role or name or xpath:
            node = self._find_uia(
                automation_id=automation_id,
                role=role,
                name=name,
                xpath=xpath,
            )
            node["text"] = text
            return
        unsupported(self.driver_name, "type_text", detail="provide automation_id or role+name")

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
        self.click(
            role=role,
            name=name,
            test_id=test_id,
            automation_id=automation_id,
            css=css,
            xpath=xpath,
            image=image,
            x=x,
            y=y,
        )

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
    ) -> None:
        _ = timeout_s
        node = self._find_uia(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        if until == "visible" and not node.get("visible"):
            raise TimeoutError("sim control not visible")
        if until == "enabled" and not node.get("enabled"):
            raise TimeoutError("sim control not enabled")
        if until == "text" and text is not None and node.get("text") != text:
            raise TimeoutError("sim control text mismatch")

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        _ = timeout_s
        time.sleep(0.01)

    def capture_screenshot(self, *, path: Path) -> Path:
        rgb = bytearray(solid_rgb(self._width, self._height, self._color))
        bx, by, bw, bh = self._button_rect
        for row in range(by, by + bh):
            for col in range(bx, bx + bw):
                off = (row * self._width + col) * 3
                rgb[off : off + 3] = bytes((0, 180, 0))
        write_png(path, self._width, self._height, bytes(rgb))
        return path

    def capture_tree(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "windows": [{"title": self.title, "x": 0, "y": 0, "w": self._width, "h": self._height}],
            "controls": list(self._uia.values()),
        }

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> str:
        node = self._find_uia(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        return str(node.get("text", ""))

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool:
        return bool(
            self._find_uia(
                automation_id=automation_id,
                role=role,
                name=name,
                xpath=xpath,
            ).get("visible"),
        )

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool:
        return bool(
            self._find_uia(
                automation_id=automation_id,
                role=role,
                name=name,
                xpath=xpath,
            ).get("enabled"),
        )

    def capture_meta(self) -> dict[str, Any]:
        return {
            "driver": self.driver_name,
            "desktop_id": self.desktop_id,
            "title": self.title,
            "width": self._width,
            "height": self._height,
            "dpi_scale": float(self.config.get("dpi_scale") or 1.0),
            "last_click": self._last_click,
        }

    def render_button_template(self, path: Path) -> Path:
        """Write the green button crop used by image-match catalog examples."""
        bx, by, bw, bh = self._button_rect
        write_png(path, bw, bh, solid_rgb(bw, bh, (0, 180, 0)))
        return path

    # Alias used by unit tests / catalog helpers.
    write_button_template = render_button_template

    def _click_image(self, image: str) -> None:
        shot = Path(image)
        # If path is a template, match against current framebuffer.
        frame = bytearray(solid_rgb(self._width, self._height, self._color))
        bx, by, bw, bh = self._button_rect
        for row in range(by, by + bh):
            for col in range(bx, bx + bw):
                off = (row * self._width + col) * 3
                frame[off : off + 3] = bytes((0, 180, 0))
        nw, nh, needle = read_png(shot)
        hit = find_template(bytes(frame), self._width, self._height, needle, nw, nh)
        if hit is None:
            raise LookupError(f"sim image template not found: {image}")
        self._last_click = (float(hit[0] + nw / 2), float(hit[1] + nh / 2))

    def _find_uia(
        self,
        *,
        automation_id: str | None,
        role: str | None,
        name: str | None,
        xpath: str | None = None,
    ) -> dict[str, Any]:
        if xpath is not None:
            auto_id = _automation_id_from_xpath(xpath)
            if auto_id is not None:
                automation_id = auto_id
        if automation_id is not None:
            node = self._uia.get(automation_id)
            if node is None:
                raise LookupError(f"sim automation_id not found: {automation_id}")
            return node
        for node in self._uia.values():
            if role is not None and node.get("role") != role:
                continue
            if name is not None and node.get("name") != name:
                continue
            if role is not None or name is not None:
                return node
        unsupported(
            self.driver_name,
            "uia_locate",
            detail="provide automation_id or role+name",
        )
        raise AssertionError("unreachable")

    @staticmethod
    def _reject_web_locators(
        *,
        css: str | None,
        test_id: str | None,
    ) -> None:
        if css is not None or test_id is not None:
            raise ValueError("css/test_id are web-only; use col.gui.web")


def _automation_id_from_xpath(xpath: str) -> str | None:
    marker = "@AutomationId='"
    if marker not in xpath:
        return None
    start = xpath.index(marker) + len(marker)
    end = xpath.index("'", start)
    return xpath[start:end]
