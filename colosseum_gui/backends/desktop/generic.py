"""Best-effort desktop backend: screenshots, image/coord click, keys.

Windows uses SendInput; Linux uses X11 / XTest (``driver=generic`` or ``x11``).
Tree locators (automation_id / UIA role) raise :class:`GuiCapabilityError`.
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from colosseum_gui.capabilities import unsupported
from colosseum_gui.exceptions import GuiConnectionError
from colosseum_gui.visual import find_template
from colosseum_gui.visual.pngutil import read_png


class GenericDesktopBackend:
    """Portable pixel/mouse desktop surface (no accessibility tree)."""

    driver_name = "generic"

    def __init__(self, *, desktop_id: int, config: dict[str, Any]) -> None:
        self.desktop_id = desktop_id
        self.config = dict(config)
        self.title = str(config.get("title") or "")
        self._dpi_scale = float(config.get("dpi_scale") or 1.0)
        self._timeout_s = float(config.get("timeout_s") or 10.0)
        self._impl: _OsDesktop
        if sys.platform.startswith("win"):
            self._impl = _WindowsDesktop(title=self.title)
        elif sys.platform.startswith("linux"):
            display = str(config.get("display") or os.environ.get("DISPLAY") or "")
            if not display:
                raise OSError(
                    "generic desktop on Linux requires $DISPLAY "
                    "(X11 or XWayland); set display= in [[gui.desktop]] or export DISPLAY",
                )
            self._impl = _LinuxX11Desktop(title=self.title, display=display)
        else:
            raise OSError(f"generic desktop is not supported on {sys.platform}")

    def close(self) -> None:
        self._impl.close()

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
        self._reject_web_and_uia(
            role=role,
            name=name,
            test_id=test_id,
            automation_id=automation_id,
            css=css,
            xpath=xpath,
        )
        _ = input  # generic is always mouse
        if image is not None:
            ax, ay = self._locate_image(image)
            self._impl.click_at(ax, ay)
            return
        if x is not None and y is not None:
            self._impl.click_at(float(x), float(y))
            return
        unsupported(
            self.driver_name,
            "click",
            detail="provide image= or x+y (UIA locators need driver=pywinauto)",
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
        self._reject_web_and_uia(
            role=role,
            name=name,
            test_id=test_id,
            automation_id=automation_id,
            css=css,
            xpath=xpath,
        )
        _ = input
        if image is not None:
            ax, ay = self._locate_image(image)
            self._impl.click_at(ax, ay)
        elif x is not None and y is not None:
            self._impl.click_at(float(x), float(y))
        self._impl.type_text(text)

    def press_key(self, *, key: str) -> None:
        self._impl.press_key(key)

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
        self._reject_web_and_uia(
            role=role,
            name=name,
            test_id=test_id,
            automation_id=automation_id,
            css=css,
            xpath=xpath,
        )
        if image is not None:
            ax, ay = self._locate_image(image)
            self._impl.move_to(ax, ay)
            return
        if x is not None and y is not None:
            self._impl.move_to(float(x), float(y))
            return
        unsupported(self.driver_name, "hover", detail="provide image= or x+y")

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
        _ = (until, timeout_s, role, name, automation_id, text)
        unsupported(
            self.driver_name,
            "wait",
            detail="tree waits require driver=pywinauto; use wait_stable",
        )

    def wait_stable(self, *, timeout_s: float = 2.0) -> None:
        deadline = time.monotonic() + timeout_s
        previous: bytes | None = None
        while time.monotonic() < deadline:
            current = self._impl.grab_png_bytes()
            if previous is not None and current == previous:
                return
            previous = current
            time.sleep(0.1)

    def capture_screenshot(self, *, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self._impl.grab_png_bytes())
        return path

    def capture_tree(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "windows": self._impl.list_windows(),
            "note": "generic driver has no control tree; use driver=pywinauto on Windows",
        }

    def get_text(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> str:
        _ = (role, name, automation_id)
        unsupported(self.driver_name, "get_text", detail="requires driver=pywinauto")

    def is_visible(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> bool:
        _ = (role, name, automation_id)
        unsupported(self.driver_name, "is_visible", detail="requires driver=pywinauto")

    def is_enabled(
        self,
        *,
        role: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ) -> bool:
        _ = (role, name, automation_id)
        unsupported(self.driver_name, "is_enabled", detail="requires driver=pywinauto")

    def capture_meta(self) -> dict[str, Any]:
        geom = self._impl.window_geometry()
        return {
            "driver": self.driver_name,
            "desktop_id": self.desktop_id,
            "title": self.title,
            "dpi_scale": self._dpi_scale,
            **geom,
        }

    def _locate_image(self, image: str) -> tuple[float, float]:
        template = Path(image)
        if not template.is_file():
            raise FileNotFoundError(image)
        # Capture to a temp buffer via PNG round-trip on disk under the process cwd is
        # avoided; decode grab bytes through a NamedTemporaryFile-like path write.
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
            tmp = Path(handle.name)
        try:
            tmp.write_bytes(self._impl.grab_png_bytes())
            hw, hh, hay = read_png(tmp)
            nw, nh, needle = read_png(template)
        finally:
            tmp.unlink(missing_ok=True)
        hit = find_template(hay, hw, hh, needle, nw, nh)
        if hit is None:
            raise LookupError(f"image template not found: {image}")
        origin = self._impl.window_origin()
        return origin[0] + hit[0] + nw / 2.0, origin[1] + hit[1] + nh / 2.0

    @staticmethod
    def _reject_web_and_uia(
        *,
        role: str | None,
        name: str | None,
        test_id: str | None,
        automation_id: str | None,
        css: str | None,
        xpath: str | None,
    ) -> None:
        if css is not None or xpath is not None or test_id is not None:
            raise ValueError("css/xpath/test_id are web-only; use col.gui.web")
        if automation_id is not None or role is not None or name is not None:
            unsupported(
                "generic",
                "uia_locate",
                detail="automation_id/role/name require driver=pywinauto",
            )


class _OsDesktop:
    def close(self) -> None:
        return None

    def click_at(self, x: float, y: float) -> None:
        raise NotImplementedError

    def move_to(self, x: float, y: float) -> None:
        raise NotImplementedError

    def type_text(self, text: str) -> None:
        raise NotImplementedError

    def press_key(self, key: str) -> None:
        raise NotImplementedError

    def grab_png_bytes(self) -> bytes:
        raise NotImplementedError

    def list_windows(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def window_geometry(self) -> dict[str, Any]:
        raise NotImplementedError

    def window_origin(self) -> tuple[float, float]:
        raise NotImplementedError


def _win_user32() -> Any:  # noqa: ANN401
    """Resolve ctypes.windll.user32 without assuming Windows stubs (CI is Linux)."""
    import ctypes

    windll = getattr(ctypes, "windll", None)
    if windll is None:  # pragma: no cover - Windows-only path
        raise RuntimeError("ctypes.windll is only available on Windows")
    return windll.user32


def _win_func_type(*args: object) -> Any:  # noqa: ANN401
    """Resolve ctypes.WINFUNCTYPE without assuming Windows stubs."""
    import ctypes

    factory = getattr(ctypes, "WINFUNCTYPE", None)
    if factory is None:  # pragma: no cover - Windows-only path
        raise RuntimeError("ctypes.WINFUNCTYPE is only available on Windows")
    return factory(*args)


class _WindowsDesktop(_OsDesktop):
    def __init__(self, *, title: str) -> None:
        self.title = title
        self._hwnd: int | None = None
        if title:
            self._hwnd = self._find_hwnd(title)

    def close(self) -> None:
        return None

    def click_at(self, x: float, y: float) -> None:
        self.move_to(x, y)
        self._mouse_event(0x0002)  # LEFTDOWN
        self._mouse_event(0x0004)  # LEFTUP

    def move_to(self, x: float, y: float) -> None:
        _win_user32().SetCursorPos(int(x), int(y))

    def type_text(self, text: str) -> None:
        user32 = _win_user32()
        for ch in text:
            vk = user32.VkKeyScanW(ord(ch))
            if vk == -1:
                continue
            code = vk & 0xFF
            self._key_event(code, key_up=False)
            self._key_event(code, key_up=True)

    def press_key(self, key: str) -> None:
        code = _VK_MAP.get(key.lower())
        if code is None:
            raise ValueError(f"unsupported key {key!r}")
        self._key_event(code, key_up=False)
        self._key_event(code, key_up=True)

    def grab_png_bytes(self) -> bytes:
        return _mss_grab(monitor=self._monitor_region())

    def list_windows(self) -> list[dict[str, Any]]:
        import ctypes
        from ctypes import wintypes

        user32 = _win_user32()
        results: list[dict[str, Any]] = []

        @_win_func_type(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)  # type: ignore[untyped-decorator]
        def _enum(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            results.append(
                {
                    "title": buf.value,
                    "x": int(rect.left),
                    "y": int(rect.top),
                    "w": int(rect.right - rect.left),
                    "h": int(rect.bottom - rect.top),
                },
            )
            return True

        user32.EnumWindows(_enum, 0)
        if self.title:
            return [w for w in results if self.title.lower() in str(w["title"]).lower()]
        return results

    def window_geometry(self) -> dict[str, Any]:
        region = self._monitor_region()
        return {
            "width": region["width"],
            "height": region["height"],
            "x": region["left"],
            "y": region["top"],
        }

    def window_origin(self) -> tuple[float, float]:
        region = self._monitor_region()
        return float(region["left"]), float(region["top"])

    def _monitor_region(self) -> dict[str, int]:
        if self._hwnd is None:
            return {"left": 0, "top": 0, "width": 0, "height": 0}
        from ctypes import byref, wintypes

        rect = wintypes.RECT()
        _win_user32().GetWindowRect(self._hwnd, byref(rect))
        return {
            "left": int(rect.left),
            "top": int(rect.top),
            "width": int(rect.right - rect.left),
            "height": int(rect.bottom - rect.top),
        }

    @staticmethod
    def _find_hwnd(title: str) -> int:
        import ctypes
        from ctypes import wintypes

        user32 = _win_user32()
        found: list[int] = []

        @_win_func_type(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)  # type: ignore[untyped-decorator]
        def _enum(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if title.lower() in buf.value.lower():
                found.append(int(hwnd))
                return False
            return True

        user32.EnumWindows(_enum, 0)
        if not found:
            raise GuiConnectionError(f"window title not found: {title!r}")
        return found[0]

    @staticmethod
    def _mouse_event(flags: int) -> None:
        _win_user32().mouse_event(flags, 0, 0, 0, 0)

    @staticmethod
    def _key_event(vk: int, *, key_up: bool) -> None:
        flags = 0x0002 if key_up else 0
        _win_user32().keybd_event(vk, 0, flags, 0)


class _LinuxX11Desktop(_OsDesktop):
    def __init__(self, *, title: str, display: str) -> None:
        try:
            from Xlib import X
            from Xlib import display as xdisplay
            from Xlib.ext import xtest
        except ImportError as exc:  # pragma: no cover
            raise GuiConnectionError(
                "python-xlib is not installed; reinstall colosseum-gui on Linux "
                "(python-xlib is a required dependency on linux)",
            ) from exc

        self.title = title
        self._X = X
        self._xtest = xtest
        os.environ.setdefault("DISPLAY", display)
        self._disp = xdisplay.Display(display)
        self._root = self._disp.screen().root
        self._window = self._find_window(title) if title else None

    def close(self) -> None:
        with suppress(Exception):
            self._disp.close()

    def click_at(self, x: float, y: float) -> None:
        self.move_to(x, y)
        self._xtest.fake_input(self._disp, self._X.ButtonPress, 1)
        self._disp.sync()
        self._xtest.fake_input(self._disp, self._X.ButtonRelease, 1)
        self._disp.sync()

    def move_to(self, x: float, y: float) -> None:
        self._xtest.fake_input(self._disp, self._X.MotionNotify, x=int(x), y=int(y))
        self._disp.sync()

    def type_text(self, text: str) -> None:
        for ch in text:
            self.press_key(ch if len(ch) == 1 else "space")

    def press_key(self, key: str) -> None:
        from Xlib import XK

        keysym = XK.string_to_keysym(key) if len(key) > 1 else XK.string_to_keysym(key)
        if keysym == 0 and len(key) == 1:
            keysym = ord(key)
        code = self._disp.keysym_to_keycode(keysym)
        if not code:
            raise ValueError(f"unsupported key {key!r}")
        self._xtest.fake_input(self._disp, self._X.KeyPress, code)
        self._disp.sync()
        self._xtest.fake_input(self._disp, self._X.KeyRelease, code)
        self._disp.sync()

    def grab_png_bytes(self) -> bytes:
        return _mss_grab(monitor=self._monitor_region())

    def list_windows(self) -> list[dict[str, Any]]:
        windows: list[dict[str, Any]] = []
        for win in self._root.query_tree().children:
            try:
                name = win.get_wm_name()
            except Exception:  # noqa: BLE001
                continue
            if not name:
                continue
            geom = win.get_geometry()
            entry = {
                "title": name,
                "x": int(geom.x),
                "y": int(geom.y),
                "w": int(geom.width),
                "h": int(geom.height),
            }
            if self.title and self.title.lower() not in str(name).lower():
                continue
            windows.append(entry)
        return windows

    def window_geometry(self) -> dict[str, Any]:
        region = self._monitor_region()
        return {
            "width": region["width"],
            "height": region["height"],
            "x": region["left"],
            "y": region["top"],
        }

    def window_origin(self) -> tuple[float, float]:
        region = self._monitor_region()
        return float(region["left"]), float(region["top"])

    def _monitor_region(self) -> dict[str, int]:
        if self._window is None:
            geom = self._root.get_geometry()
            return {
                "left": 0,
                "top": 0,
                "width": int(geom.width),
                "height": int(geom.height),
            }
        geom = self._window.get_geometry()
        return {
            "left": int(geom.x),
            "top": int(geom.y),
            "width": int(geom.width),
            "height": int(geom.height),
        }

    def _find_window(self, title: str) -> Any:  # noqa: ANN401
        for win in self._root.query_tree().children:
            try:
                name = win.get_wm_name()
            except Exception:  # noqa: BLE001
                continue
            if name and title.lower() in str(name).lower():
                return win
        raise GuiConnectionError(f"window title not found: {title!r}")


def _mss_grab(*, monitor: dict[str, int]) -> bytes:
    try:
        import mss
        import mss.tools
    except ImportError as exc:  # pragma: no cover
        raise GuiConnectionError(
            "mss is not installed; reinstall colosseum-gui "
            "(mss is a required dependency)",
        ) from exc

    with mss.mss() as sct:
        if monitor.get("width", 0) <= 0 or monitor.get("height", 0) <= 0:
            shot = sct.grab(sct.monitors[1])
        else:
            shot = sct.grab(monitor)
        png = mss.tools.to_png(shot.rgb, shot.size)
        if png is None:
            raise GuiConnectionError("mss failed to encode PNG screenshot")
        return bytes(png)


_VK_MAP = {
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "escape": 0x1B,
    "esc": 0x1B,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
}
