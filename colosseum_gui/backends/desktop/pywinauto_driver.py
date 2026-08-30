"""Windows UI Automation desktop backend via pywinauto."""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING, Any

from colosseum_gui.capabilities import unsupported
from colosseum_gui.exceptions import GuiConnectionError

if TYPE_CHECKING:
    from pathlib import Path


class PywinautoDesktopBackend:
    """Drive a Windows window with pywinauto UIA (Windows only)."""

    driver_name = "pywinauto"

    # Declared at class scope so Linux mypy (sys.platform != win) still types methods.
    desktop_id: int
    config: dict[str, Any]
    title: str
    _owns_app: bool
    _app: Any
    _window: Any

    def __init__(self, *, desktop_id: int, config: dict[str, Any]) -> None:
        if not sys.platform.startswith("win"):
            raise OSError("pywinauto is only available on Windows")
        try:
            from pywinauto import Application
        except ImportError as exc:  # pragma: no cover
            raise GuiConnectionError(
                "pywinauto is not installed; reinstall colosseum-gui on Windows "
                "(pywinauto is a required dependency on win32)",
            ) from exc

        self.desktop_id = desktop_id
        self.config = dict(config)
        self.title = str(config.get("title") or "")
        backend = str(config.get("uia_backend") or "uia")
        timeout_s = float(config.get("timeout_s") or 10.0)
        exe = config.get("exe")
        process_id = config.get("process_id")
        self._owns_app = False

        if exe:
            self._app = Application(backend=backend).start(str(exe))
            self._owns_app = True
        elif process_id not in (None, ""):
            self._app = Application(backend=backend).connect(process=int(str(process_id)))
        elif self.title:
            self._app = Application(backend=backend).connect(title_re=f".*{self.title}.*")
        else:
            raise GuiConnectionError(
                "pywinauto requires exe=, process_id=, or title= in [[gui.desktop]]",
            )
        self._window = self._app.top_window()
        self._window.wait("ready", timeout=timeout_s)

    def close(self) -> None:
        if self._owns_app:
            self._app.kill(soft=False)

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
        self._reject_web(css=css, xpath=xpath, test_id=test_id)
        if image is not None or (x is not None and y is not None):
            # Explicit mouse path without UIA.
            if image is not None:
                unsupported(
                    self.driver_name,
                    "click_image",
                    detail="use driver=generic for image clicks",
                )
            self._window.click_input(coords=(int(x or 0), int(y or 0)))
            return
        ctrl = self._find(automation_id=automation_id, role=role, name=name)
        if (input or "invoke") == "mouse":
            ctrl.click_input()
        else:
            try:
                ctrl.invoke()
            except Exception:  # noqa: BLE001 - fall back to click_input once
                ctrl.click_input()

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
        self._reject_web(css=css, xpath=xpath, test_id=test_id)
        _ = (image, x, y)
        ctrl = self._find(automation_id=automation_id, role=role, name=name)
        if (input or "invoke") == "keys":
            ctrl.type_keys(text, with_spaces=True)
        else:
            try:
                ctrl.set_edit_text(text)
            except Exception:  # noqa: BLE001
                ctrl.type_keys(text, with_spaces=True)

    def press_key(self, *, key: str) -> None:
        self._window.type_keys(f"{{{key.upper()}}}")

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
        self._reject_web(css=css, xpath=xpath, test_id=test_id)
        _ = (image, x, y)
        ctrl = self._find(automation_id=automation_id, role=role, name=name)
        rect = ctrl.rectangle()
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        self._window.move_mouse(coords=(cx, cy))

    def wait(
        self,
        *,
        until: str,
        timeout_s: float = 10.0,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        text: str | None = None,
    ) -> None:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                ctrl = self._find(automation_id=automation_id, role=role, name=name)
                if until == "visible" and ctrl.is_visible():
                    return
                if until == "enabled" and ctrl.is_enabled():
                    return
                if until == "text" and text is not None:
                    actual = self._control_text(ctrl)
                    if actual == text:
                        return
            except Exception:  # noqa: BLE001 - keep polling
                pass
            time.sleep(0.1)
        raise TimeoutError(f"wait until={until!r} timed out")

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        deadline = time.monotonic() + timeout_s
        previous: tuple[int, int, int, int] | None = None
        while time.monotonic() < deadline:
            rect = self._window.rectangle()
            current = (rect.left, rect.top, rect.right, rect.bottom)
            if previous == current:
                return
            previous = current
            time.sleep(0.1)

    def capture_screenshot(self, *, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._window.capture_as_image().save(str(path))
        return path

    def capture_tree(self) -> dict[str, Any]:
        nodes: list[dict[str, Any]] = []

        def walk(ctrl: Any, depth: int = 0) -> None:  # noqa: ANN401
            try:
                nodes.append(
                    {
                        "depth": depth,
                        "name": str(ctrl.window_text()),
                        "automation_id": str(getattr(ctrl.element_info, "automation_id", "")),
                        "control_type": str(getattr(ctrl.element_info, "control_type", "")),
                        "visible": bool(ctrl.is_visible()),
                        "enabled": bool(ctrl.is_enabled()),
                    },
                )
            except Exception:  # noqa: BLE001
                return
            try:
                children = ctrl.children()
            except Exception:  # noqa: BLE001
                return
            for child in children:
                walk(child, depth + 1)

        walk(self._window)
        return {"title": self.title or self._window.window_text(), "controls": nodes}

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> str:
        return self._control_text(self._find(automation_id=automation_id, role=role, name=name))

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> bool:
        return bool(self._find(automation_id=automation_id, role=role, name=name).is_visible())

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> bool:
        return bool(self._find(automation_id=automation_id, role=role, name=name).is_enabled())

    def capture_meta(self) -> dict[str, Any]:
        rect = self._window.rectangle()
        return {
            "driver": self.driver_name,
            "desktop_id": self.desktop_id,
            "title": self.title or self._window.window_text(),
            "x": int(rect.left),
            "y": int(rect.top),
            "width": int(rect.width()),
            "height": int(rect.height()),
            "dpi_scale": float(self.config.get("dpi_scale") or 1.0),
        }

    def _find(
        self,
        *,
        automation_id: str | None,
        role: str | None,
        name: str | None,
    ) -> Any:  # noqa: ANN401
        kwargs: dict[str, Any] = {}
        if automation_id is not None:
            kwargs["auto_id"] = automation_id
        if name is not None:
            kwargs["title"] = name
        if role is not None:
            kwargs["control_type"] = _role_to_control_type(role)
        if not kwargs:
            unsupported(
                self.driver_name,
                "locate",
                detail="provide automation_id or role+name",
            )
        return self._window.child_window(**kwargs).wrapper_object()

    @staticmethod
    def _control_text(ctrl: Any) -> str:  # noqa: ANN401
        try:
            return str(ctrl.window_text())
        except Exception:  # noqa: BLE001
            return ""

    @staticmethod
    def _reject_web(*, css: str | None, xpath: str | None, test_id: str | None) -> None:
        if css is not None or xpath is not None or test_id is not None:
            raise ValueError("css/xpath/test_id are web-only; use col.gui.web")


def _role_to_control_type(role: str) -> str:
    mapping = {
        "button": "Button",
        "text": "Text",
        "edit": "Edit",
        "checkbox": "CheckBox",
        "radio": "RadioButton",
        "combobox": "ComboBox",
        "list": "List",
        "listitem": "ListItem",
        "menu": "Menu",
        "menuitem": "MenuItem",
        "window": "Window",
        "pane": "Pane",
        "tab": "Tab",
        "tabitem": "TabItem",
        "status": "StatusBar",
    }
    return mapping.get(role.lower(), role)
