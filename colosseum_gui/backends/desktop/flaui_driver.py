"""Windows UI Automation desktop backend via FlaUI + pythonnet."""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from colosseum_gui.backends.desktop._flaui_bridge import setup_flaui_bridge, uia3_automation
from colosseum_gui.capabilities import unsupported
from colosseum_gui.exceptions import GuiConnectionError
from colosseum_gui.visual import find_template
from colosseum_gui.visual.pngutil import read_png


class FlaUIDesktopBackend:
    """Drive a Windows window with FlaUI UIA3 (Windows only)."""

    driver_name = "flaui"

    desktop_id: int
    config: dict[str, Any]
    title: str
    _owns_app: bool
    _app: Any
    _window: Any
    _automation: Any

    def __init__(self, *, desktop_id: int, config: dict[str, Any]) -> None:
        if not sys.platform.startswith("win"):
            raise OSError("flaui is only available on Windows")
        try:
            setup_flaui_bridge()
            from FlaUI.Core import Application
            from FlaUI.Core.Definitions import ControlType
        except ImportError as exc:
            raise GuiConnectionError(
                "FlaUI bridge could not be initialized; reinstall colosseum-gui on Windows",
            ) from exc

        self._control_type: Any = ControlType
        self.desktop_id = desktop_id
        self.config = dict(config)
        self.title = str(config.get("title") or "")
        timeout_s = float(config.get("timeout_s") or 10.0)
        exe = config.get("exe")
        process_id = config.get("process_id")
        self._owns_app = False
        self._automation = uia3_automation()

        if exe:
            self._app = Application.Launch(str(exe))
            self._owns_app = True
            title_hint = self.title or Path(str(exe)).stem
            self._window = self._wait_main_window(self._app, timeout_s=min(timeout_s, 5.0))
            if self._window is None:
                # Win11 notepad.exe is a stub that exits; the editor is another PID.
                self._window = self._find_window_by_title(title_hint, timeout_s=timeout_s)
                self._reattach_to_window_process(Application)
        elif process_id not in (None, ""):
            self._app = Application.Attach(int(str(process_id)))
            self._window = self._wait_main_window(self._app, timeout_s=timeout_s)
            if self._window is None:
                raise GuiConnectionError("flaui could not obtain the application main window")
        elif self.title:
            self._app = None
            self._window = self._find_window_by_title(self.title, timeout_s=timeout_s)
        else:
            raise GuiConnectionError(
                "flaui requires exe=, process_id=, or title= in [[gui.desktop]]",
            )

    def close(self) -> None:
        if self._owns_app and self._app is not None:
            self._app.Kill()

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
        self._reject_web(css=css, test_id=test_id)
        if image is not None:
            ax, ay = self._locate_image(image)
            self._click_coords(ax, ay)
            return
        if x is not None and y is not None:
            self._click_coords(float(x), float(y))
            return
        element = self._find(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        if (input or "invoke") == "mouse":
            element.Click()
        else:
            self._invoke_element(element)

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
        self._reject_web(css=css, test_id=test_id)
        _ = (image, x, y)
        element = self._find(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        if (input or "invoke") == "keys":
            from FlaUI.Core.Input import Keyboard

            element.Focus()
            Keyboard.Type(text)
        else:
            try:
                element.AsTextBox().Enter(text)
            except Exception:  # noqa: BLE001
                element.Focus()
                from FlaUI.Core.Input import Keyboard

                Keyboard.Type(text)

    def press_key(self, *, key: str) -> None:
        from FlaUI.Core.Input import Keyboard
        from FlaUI.Core.WindowsAPI import VirtualKeyShort

        vk = getattr(VirtualKeyShort, key.upper(), None)
        if vk is None:
            Keyboard.Type(key)
            return
        Keyboard.Press(vk)

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
        self._reject_web(css=css, test_id=test_id)
        if image is not None:
            ax, ay = self._locate_image(image)
            self._move_coords(ax, ay)
            return
        if x is not None and y is not None:
            self._move_coords(float(x), float(y))
            return
        element = self._find(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        rect = element.BoundingRectangle
        self._move_coords(rect.X + rect.Width / 2.0, rect.Y + rect.Height / 2.0)

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
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                element = self._find(
                    automation_id=automation_id,
                    role=role,
                    name=name,
                    xpath=xpath,
                )
                if until == "visible" and _element_is_visible(element):
                    return
                if until == "enabled" and _element_is_enabled(element):
                    return
                if until == "text" and text is not None:
                    actual = self._element_text(element)
                    if actual == text:
                        return
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.1)
        raise TimeoutError(f"wait until={until!r} timed out")

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        deadline = time.monotonic() + timeout_s
        previous: tuple[int, int, int, int] | None = None
        while time.monotonic() < deadline:
            rect = self._window.BoundingRectangle
            current = (int(rect.X), int(rect.Y), int(rect.Width), int(rect.Height))
            if previous == current:
                return
            previous = current
            time.sleep(0.1)

    def capture_screenshot(self, *, path: Path) -> Path:
        from colosseum_gui.backends.desktop.generic import _mss_grab

        rect = self._window.BoundingRectangle
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            _mss_grab(
                monitor={
                    "left": int(rect.X),
                    "top": int(rect.Y),
                    "width": int(rect.Width),
                    "height": int(rect.Height),
                },
            ),
        )
        return path

    def capture_tree(self) -> dict[str, Any]:
        nodes: list[dict[str, Any]] = []

        def walk(element: Any, depth: int = 0) -> None:  # noqa: ANN401
            try:
                nodes.append(
                    {
                        "depth": depth,
                        "name": str(element.Name or ""),
                        "automation_id": str(element.AutomationId or ""),
                        "control_type": str(element.ControlType),
                        "visible": _element_is_visible(element),
                        "enabled": _element_is_enabled(element),
                    },
                )
            except Exception:  # noqa: BLE001
                return
            try:
                children = element.FindAllChildren()
            except Exception:  # noqa: BLE001
                return
            for child in children:
                walk(child, depth + 1)

        walk(self._window)
        return {
            "title": self.title or str(self._window.Name or ""),
            "controls": nodes,
        }

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> str:
        return self._element_text(
            self._find(automation_id=automation_id, role=role, name=name, xpath=xpath),
        )

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool:
        element = self._find(
            automation_id=automation_id,
            role=role,
            name=name,
            xpath=xpath,
        )
        return _element_is_visible(element)

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
        xpath: str | None = None,
    ) -> bool:
        return _element_is_enabled(
            self._find(
                automation_id=automation_id,
                role=role,
                name=name,
                xpath=xpath,
            ),
        )

    def capture_meta(self) -> dict[str, Any]:
        rect = self._window.BoundingRectangle
        return {
            "driver": self.driver_name,
            "desktop_id": self.desktop_id,
            "title": self.title or str(self._window.Name or ""),
            "x": int(rect.X),
            "y": int(rect.Y),
            "width": int(rect.Width),
            "height": int(rect.Height),
            "dpi_scale": float(self.config.get("dpi_scale") or 1.0),
        }

    def _wait_main_window(self, app: Any, *, timeout_s: float) -> Any:  # noqa: ANN401
        from System import TimeSpan

        try:
            return app.GetMainWindow(self._automation, TimeSpan.FromSeconds(float(timeout_s)))
        except Exception:  # noqa: BLE001 - stub launch PIDs die (Win11 Notepad)
            return None

    def _reattach_to_window_process(self, application_cls: Any) -> None:  # noqa: ANN401
        pid = int(self._window.Properties.ProcessId.Value)
        self._app = application_cls.Attach(pid)

    def _find_window_by_title(self, title: str, *, timeout_s: float) -> Any:  # noqa: ANN401
        deadline = time.monotonic() + timeout_s
        needle = title.casefold()
        cf = self._automation.ConditionFactory
        while time.monotonic() < deadline:
            desktop = self._automation.GetDesktop()
            for window in desktop.FindAllChildren(cf.ByControlType(self._control_type.Window)):
                name = str(window.Name or "")
                if needle in name.casefold():
                    return window
            time.sleep(0.1)
        raise GuiConnectionError(f"flaui could not find a window matching title={title!r}")

    def _find(
        self,
        *,
        automation_id: str | None,
        role: str | None,
        name: str | None,
        xpath: str | None,
    ) -> Any:  # noqa: ANN401
        if xpath is not None:
            element = self._window.FindFirstByXPath(xpath)
            if element is None:
                raise LookupError(f"xpath not found: {xpath}")
            return element

        cf = self._automation.ConditionFactory
        condition = None
        if automation_id is not None:
            condition = cf.ByAutomationId(automation_id)
        if name is not None:
            name_cond = cf.ByName(name)
            condition = name_cond if condition is None else condition.And(name_cond)
        if role is not None:
            role_cond = _role_condition(role, cf, self._control_type)
            condition = role_cond if condition is None else condition.And(role_cond)
        if condition is None:
            unsupported(
                self.driver_name,
                "locate",
                detail="provide automation_id, role+name, or xpath",
            )
        element = self._window.FindFirstDescendant(condition)
        if element is None:
            raise LookupError("UIA element not found")
        return element

    def _invoke_element(self, element: Any) -> None:  # noqa: ANN401
        try:
            element.Patterns.Invoke.Pattern.Invoke()
        except Exception:  # noqa: BLE001
            element.Click()

    def _element_text(self, element: Any) -> str:  # noqa: ANN401
        try:
            return str(element.Name or "")
        except Exception:  # noqa: BLE001
            return ""

    def _locate_image(self, image: str) -> tuple[float, float]:
        template = Path(image)
        if not template.is_file():
            raise FileNotFoundError(image)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
            tmp = Path(handle.name)
        try:
            self.capture_screenshot(path=tmp)
            hw, hh, hay = read_png(tmp)
            nw, nh, needle = read_png(template)
        finally:
            tmp.unlink(missing_ok=True)
        hit = find_template(hay, hw, hh, needle, nw, nh)
        if hit is None:
            raise LookupError(f"image template not found: {image}")
        rect = self._window.BoundingRectangle
        return (
            float(rect.X) + hit[0] + nw / 2.0,
            float(rect.Y) + hit[1] + nh / 2.0,
        )

    def _click_coords(self, x: float, y: float) -> None:
        from FlaUI.Core.Input import Mouse
        from FlaUI.Core.WindowsAPI import MouseButton

        Mouse.Click(int(x), int(y), MouseButton.Left)

    def _move_coords(self, x: float, y: float) -> None:
        from FlaUI.Core.Input import Mouse

        Mouse.MoveTo(int(x), int(y))

    @staticmethod
    def _reject_web(*, css: str | None, test_id: str | None) -> None:
        if css is not None or test_id is not None:
            raise ValueError("css/test_id are web-only; use col.gui.web")


def _element_is_visible(element: Any) -> bool:  # noqa: ANN401
    try:
        return element.IsOffscreen is False
    except Exception:  # noqa: BLE001 - Win11 Notepad Document omits IsOffscreen
        return True


def _element_is_enabled(element: Any) -> bool:  # noqa: ANN401
    try:
        return bool(element.IsEnabled)
    except Exception:  # noqa: BLE001
        return True


def _role_condition(role: str, condition_factory: Any, control_type: Any) -> Any:  # noqa: ANN401
    # Win10 Notepad is Edit; Win11 Notepad (WinUI) is Document.
    if role.lower() == "edit":
        return condition_factory.ByControlType(control_type.Edit).Or(
            condition_factory.ByControlType(control_type.Document),
        )
    return condition_factory.ByControlType(_role_to_control_type(role, control_type))


def _role_to_control_type(role: str, control_type: Any) -> Any:  # noqa: ANN401
    mapping = {
        "button": control_type.Button,
        "text": control_type.Text,
        "edit": control_type.Edit,
        "document": control_type.Document,
        "checkbox": control_type.CheckBox,
        "radio": control_type.RadioButton,
        "combobox": control_type.ComboBox,
        "list": control_type.List,
        "listitem": control_type.ListItem,
        "menu": control_type.Menu,
        "menuitem": control_type.MenuItem,
        "window": control_type.Window,
        "pane": control_type.Pane,
        "tab": control_type.Tab,
        "tabitem": control_type.TabItem,
        "status": control_type.StatusBar,
    }
    return mapping.get(role.lower(), control_type.Custom)
