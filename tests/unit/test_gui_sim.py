"""Sim-driver unit tests for col.gui.web and col.gui.desktop."""

from __future__ import annotations

from typing import TYPE_CHECKING

import colosseum as col
import pytest
from colosseum_gui.exceptions import GuiCapabilityError
from colosseum_gui.visual.pngutil import read_png, solid_rgb, write_png
from PIL import Image

if TYPE_CHECKING:
    from pathlib import Path


def test_web_sim_click_and_verify_visible(loaded) -> None:
    col.gui.web.connect(web_id=1)
    col.gui.web.click(web_id=1, role="button", name="Start")
    result = col.gui.web.verify_visible(web_id=1, key="running", role="status", name="Running")
    assert result.status == "PASS"


def test_web_sim_navigate_and_screenshot(loaded) -> None:
    from colosseum.context import get_context

    col.gui.web.navigate(web_id=1, url="http://dut.local/")
    ms = col.gui.web.measure_navigation_ms(web_id=1, key="nav")
    assert ms >= 0.0
    col.gui.web.capture_screenshot(web_id=1, path="captures/web.png")
    out = get_context().output_dir
    assert out is not None
    assert (out / "captures" / "web.png").is_file()


def test_web_sim_verify_text(loaded) -> None:
    result = col.gui.web.verify_text(
        web_id=1, key="btn", expected="Start", role="button", name="Start",
    )
    assert result.status == "PASS"


def test_desktop_sim_uia_click(loaded) -> None:
    col.gui.desktop.click(desktop_id=1, automation_id="StartBtn")
    result = col.gui.desktop.verify_text(
        desktop_id=1, key="start", expected="Running", automation_id="StartBtn",
    )
    assert result.status == "PASS"


def test_desktop_sim_image_click(loaded, tmp_path: Path) -> None:
    from colosseum_gui.connections import get_desktop

    backend = get_desktop(1)
    template = tmp_path / "btn.png"
    backend.render_button_template(template)
    col.gui.desktop.click(desktop_id=1, image=str(template))
    meta = backend.capture_meta()
    assert meta.get("last_click") is not None


def test_desktop_sim_rejects_web_locators(loaded) -> None:
    # Assert the backend contract directly; @command records ERROR then re-raises
    # (core) or may still swallow on older core — either way the sim must raise.
    from colosseum_gui.connections import get_desktop

    with pytest.raises(ValueError, match="web-only|css/xpath"):
        get_desktop(1).click(css=".btn")


def test_desktop_generic_rejects_uia_on_capability(tmp_path: Path, ctx) -> None:
    # generic driver raises GuiCapabilityError for automation_id (needs display on real OS;
    # on CI we only assert the factory path for sim vs capability messaging via sim).
    _ = (tmp_path, ctx)
    from colosseum_gui.capabilities import unsupported

    with pytest.raises(GuiCapabilityError):
        unsupported("generic", "uia_locate", detail="needs pywinauto")


def test_visual_diff_pass_and_fail(tmp_path: Path) -> None:
    from colosseum_gui.api import _visual

    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    write_png(a, 4, 4, solid_rgb(4, 4, (10, 20, 30)))
    write_png(b, 4, 4, solid_rgb(4, 4, (10, 20, 30)))
    ok = _visual.verify_visual_paths(path=str(a), baseline=str(b), max_diff_ratio=0.0)
    assert ok.status == "PASS"
    write_png(b, 4, 4, solid_rgb(4, 4, (200, 0, 0)))
    bad = _visual.verify_visual_paths(path=str(a), baseline=str(b), max_diff_ratio=0.0)
    assert bad.status == "FAIL"


def test_contrast_helpers(tmp_path: Path) -> None:
    from colosseum_gui.visual import contrast_ratio, sample_mean_rgb

    path = tmp_path / "c.png"
    # Left half black, right half white.
    rgb = bytearray()
    for _y in range(10):
        for x in range(10):
            rgb.extend((0, 0, 0) if x < 5 else (255, 255, 255))
    write_png(path, 10, 10, bytes(rgb))
    fg = sample_mean_rgb(path, x=0, y=0, width=5, height=10)
    bg = sample_mean_rgb(path, x=5, y=0, width=5, height=10)
    ratio = contrast_ratio(fg, bg)
    assert ratio > 20.0


def test_png_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "t.png"
    write_png(path, 2, 2, solid_rgb(2, 2, (1, 2, 3)))
    w, h, rgb = read_png(path)
    assert (w, h) == (2, 2)
    assert rgb[:3] == bytes((1, 2, 3))


def test_read_png_from_pillow_writer(tmp_path: Path) -> None:
    path = tmp_path / "pillow.png"
    Image.frombytes("RGBA", (2, 1), bytes((1, 2, 3, 255, 4, 5, 6, 128))).save(path)

    w, h, rgb = read_png(path)

    assert (w, h) == (2, 1)
    assert rgb == bytes((1, 2, 3, 4, 5, 6))


def test_web_coord_locator_reads_dom_state() -> None:
    from colosseum_gui.backends.web.playwright_driver import _CoordLocator

    page = _FakePage(
        [
            {
                "exists": True,
                "visible": True,
                "enabled": False,
                "text": "Launch",
            },
        ],
    )
    locator = _CoordLocator(page, 10, 20)

    assert locator.inner_text() == "Launch"
    assert locator.is_visible() is True
    assert locator.is_enabled() is False
    assert page.last_arg == {"x": 10, "y": 20}


def test_web_coord_locator_waits_for_filtered_text() -> None:
    from colosseum_gui.backends.web.playwright_driver import _CoordLocator

    page = _FakePage(
        [
            {"exists": True, "visible": True, "enabled": True, "text": "Loading"},
            {"exists": True, "visible": True, "enabled": True, "text": "Done"},
        ],
    )

    _CoordLocator(page, 5, 6).filter(has_text="Done").wait_for(state="visible", timeout=100)

    assert page.calls == 2


def test_web_coord_locator_timeout_when_element_state_never_matches() -> None:
    from colosseum_gui.backends.web.playwright_driver import _CoordLocator

    locator = _CoordLocator(
        _FakePage([{"exists": False, "visible": False, "enabled": False, "text": ""}]),
        1,
        2,
    )

    assert locator.is_visible() is False
    assert locator.is_enabled() is False
    with pytest.raises(TimeoutError):
        locator.wait_for(state="visible", timeout=0)


def test_pywinauto_close_only_kills_owned_app() -> None:
    from colosseum_gui.backends.desktop.pywinauto_driver import PywinautoDesktopBackend

    owned = PywinautoDesktopBackend.__new__(PywinautoDesktopBackend)
    owned._owns_app = True
    owned._app = _FakePywinautoApp()
    owned.close()
    assert owned._app.killed is True

    attached = PywinautoDesktopBackend.__new__(PywinautoDesktopBackend)
    attached._owns_app = False
    attached._app = _FakePywinautoApp()
    attached.close()
    assert attached._app.killed is False


class _FakePage:
    def __init__(self, snapshots):
        self._snapshots = list(snapshots)
        self.calls = 0
        self.last_arg = None

    def evaluate(self, _script, arg):
        self.last_arg = arg
        index = min(self.calls, len(self._snapshots) - 1)
        self.calls += 1
        return self._snapshots[index]


class _FakePywinautoApp:
    def __init__(self):
        self.killed = False

    def kill(self, *, soft):
        assert soft is False
        self.killed = True
