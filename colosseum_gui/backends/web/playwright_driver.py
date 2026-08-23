"""Playwright sync web backend."""

from __future__ import annotations

import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from colosseum_gui.exceptions import GuiConnectionError


class PlaywrightWebBackend:
    """Drive a browser page with Playwright (Linux and Windows)."""

    driver_name = "playwright"

    def __init__(self, *, web_id: int, config: dict[str, Any]) -> None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - install/env issue
            raise GuiConnectionError(
                "playwright is not installed; reinstall colosseum-gui "
                "(playwright is a required dependency)"
            ) from exc

        self.web_id = web_id
        self.config = dict(config)
        self._timeout_ms = int(float(config.get("timeout_s") or 10.0) * 1000)
        headed_raw = config.get("headed", False)
        headed = str(headed_raw).lower() in ("1", "true", "yes", "on")
        browser_name = str(config.get("browser") or "chromium").lower()
        cdp_url = config.get("cdp_url")
        url = str(config.get("url") or "about:blank")

        self._pw = sync_playwright().start()
        self._owns_browser = True
        if cdp_url:
            self._browser = self._pw.chromium.connect_over_cdp(str(cdp_url))
            self._owns_browser = False
            contexts = self._browser.contexts
            self._context = contexts[0] if contexts else self._browser.new_context()
            pages = self._context.pages
            self._page = pages[0] if pages else self._context.new_page()
        else:
            launcher = getattr(self._pw, browser_name, None)
            if launcher is None:
                self.close()
                raise GuiConnectionError(f"unsupported playwright browser `{browser_name}`")
            self._browser = launcher.launch(headless=not headed)
            viewport = config.get("viewport")
            context_kwargs: dict[str, Any] = {}
            if viewport:
                # Accept "1280x720" strings.
                parts = str(viewport).lower().split("x")
                if len(parts) == 2:
                    context_kwargs["viewport"] = {
                        "width": int(parts[0]),
                        "height": int(parts[1]),
                    }
            self._context = self._browser.new_context(**context_kwargs)
            self._page = self._context.new_page()
            self._page.set_default_timeout(self._timeout_ms)
            if url and url != "about:blank":
                self._page.goto(url, wait_until="domcontentloaded")
        self._last_nav_ms = 0.0

    def close(self) -> None:
        for closer in (
            getattr(self, "_context", None),
            getattr(self, "_browser", None) if getattr(self, "_owns_browser", True) else None,
            getattr(self, "_pw", None),
        ):
            if closer is None:
                continue
            with suppress(Exception):
                closer.close()

    def navigate(self, *, url: str) -> None:
        started = time.perf_counter()
        self._page.goto(url, wait_until="domcontentloaded")
        self._last_nav_ms = (time.perf_counter() - started) * 1000.0

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
        _ = (automation_id, image)
        locator = self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        )
        force = (input or "invoke") == "mouse"
        locator.click(force=force)

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
        _ = (automation_id, image, input)
        locator = self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        )
        locator.fill(text)

    def press_key(self, *, key: str) -> None:
        self._page.keyboard.press(key)

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
        _ = (automation_id, image)
        locator = self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        )
        locator.hover()

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
        locator = self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        )
        timeout_ms = int(timeout_s * 1000)
        if until == "visible":
            locator.wait_for(state="visible", timeout=timeout_ms)
        elif until == "enabled":
            # Playwright has no dedicated enabled wait; poll is_enabled.
            deadline = time.monotonic() + timeout_s
            while time.monotonic() < deadline:
                if locator.is_enabled():
                    return
                time.sleep(0.05)
            raise TimeoutError("element did not become enabled")
        elif until == "text":
            if text is None:
                raise ValueError("wait until=text requires text=")
            locator.filter(has_text=text).wait_for(state="visible", timeout=timeout_ms)
        else:
            raise ValueError(f"unsupported wait until={until!r}")

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        deadline = time.monotonic() + timeout_s
        previous: bytes | None = None
        while time.monotonic() < deadline:
            current = self._page.screenshot(type="png")
            if previous is not None and current == previous:
                return
            previous = current
            time.sleep(0.1)
        # Timed out without two identical frames; still return (best-effort settle).

    def capture_screenshot(self, *, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._page.screenshot(path=str(path), type="png")
        return path

    def capture_tree(self) -> dict[str, Any]:
        snapshot = self._page.accessibility.snapshot()
        return {"url": self._page.url, "accessibility": snapshot}

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
        return str(self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        ).inner_text())

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
        return bool(self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        ).is_visible())

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
        return bool(self._locator(
            role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
        ).is_enabled())

    def measure_navigation_ms(self) -> float:
        return float(self._last_nav_ms)

    def capture_meta(self) -> dict[str, Any]:
        size = self._page.viewport_size or {"width": 0, "height": 0}
        return {
            "driver": self.driver_name,
            "web_id": self.web_id,
            "url": self._page.url,
            "width": size.get("width", 0),
            "height": size.get("height", 0),
            "dpi_scale": 1.0,
        }

    def _locator(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        test_id: str | None = None,
        css: str | None = None,
        xpath: str | None = None,
        x: float | None = None,
        y: float | None = None,
    ) -> Any:  # noqa: ANN401
        if x is not None and y is not None and role is None and name is None and not (
            test_id or css or xpath
        ):
            # Coordinate click uses page.mouse, exposed via a thin wrapper locator.
            return _CoordLocator(self._page, x, y)
        if test_id is not None:
            return self._page.get_by_test_id(test_id)
        if role is not None:
            kwargs: dict[str, Any] = {}
            if name is not None:
                kwargs["name"] = name
            return self._page.get_by_role(role, **kwargs)
        if css is not None:
            return self._page.locator(css)
        if xpath is not None:
            return self._page.locator(f"xpath={xpath}")
        raise ValueError("provide role(+name), test_id, css, xpath, or x+y")


class _CoordLocator:
    _ELEMENT_FROM_POINT_SCRIPT = """
({x, y}) => {
  const element = document.elementFromPoint(x, y);
  if (!element) {
    return {exists: false, visible: false, enabled: false, text: ""};
  }

  const style = window.getComputedStyle(element);
  const rects = element.getClientRects();
  const disabled =
    Boolean(element.disabled) ||
    element.getAttribute("aria-disabled") === "true" ||
    element.closest("[aria-disabled='true']") !== null;
  const text =
    "innerText" in element && element.innerText !== undefined
      ? element.innerText
      : element.textContent || "";

  return {
    exists: true,
    visible:
      rects.length > 0 &&
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || "1") > 0,
    enabled: !disabled,
    text,
  };
}
"""

    def __init__(
        self,
        page: Any,  # noqa: ANN401
        x: float,
        y: float,
        *,
        has_text: str | None = None,
    ) -> None:
        self._page = page
        self._x = x
        self._y = y
        self._has_text = has_text

    def click(self, *, force: bool = False) -> None:
        _ = force
        self._page.mouse.click(self._x, self._y)

    def fill(self, text: str) -> None:
        self._page.mouse.click(self._x, self._y)
        self._page.keyboard.type(text)

    def hover(self) -> None:
        self._page.mouse.move(self._x, self._y)

    def wait_for(self, *, state: str = "visible", timeout: float | None = None) -> None:
        timeout_s = (timeout if timeout is not None else 30000.0) / 1000.0
        deadline = time.monotonic() + timeout_s
        while True:
            snapshot = self._snapshot()
            if self._matches_state(snapshot, state):
                return
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"element at ({self._x:g}, {self._y:g}) did not become {state}"
                )
            time.sleep(0.05)

    def is_visible(self) -> bool:
        snapshot = self._snapshot()
        return bool(snapshot.get("visible")) and self._matches_text(snapshot)

    def is_enabled(self) -> bool:
        snapshot = self._snapshot()
        return bool(snapshot.get("enabled")) and self._matches_text(snapshot)

    def inner_text(self) -> str:
        return str(self._snapshot().get("text") or "")

    def filter(self, *, has_text: str | None = None) -> _CoordLocator:
        return _CoordLocator(self._page, self._x, self._y, has_text=has_text)

    def _snapshot(self) -> dict[str, Any]:
        value = self._page.evaluate(
            self._ELEMENT_FROM_POINT_SCRIPT,
            {"x": self._x, "y": self._y},
        )
        if not isinstance(value, dict):
            return {"exists": False, "visible": False, "enabled": False, "text": ""}
        return value

    def _matches_state(self, snapshot: dict[str, Any], state: str) -> bool:
        if state == "visible":
            return bool(snapshot.get("visible")) and self._matches_text(snapshot)
        if state == "attached":
            return bool(snapshot.get("exists")) and self._matches_text(snapshot)
        if state == "hidden":
            return not bool(snapshot.get("visible"))
        if state == "detached":
            return not bool(snapshot.get("exists"))
        raise ValueError(f"unsupported coordinate wait state={state!r}")

    def _matches_text(self, snapshot: dict[str, Any]) -> bool:
        if self._has_text is None:
            return True
        return self._has_text in str(snapshot.get("text") or "")
