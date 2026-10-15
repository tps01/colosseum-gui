"""Shared paths for the desktop_suite example."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
HARNESS = SUITE_DIR / "harness.py"


def artifact_dir() -> Path:
    raw = os.environ.get("COLOSSEUM_DESKTOP_SUITE_OUT")
    path = Path(raw) if raw else Path(tempfile.gettempdir()) / "colosseum_desktop_suite_out"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_gui_toml(path: Path) -> Path:
    """Write FlaUI desktops that launch this suite's tiny Tk harness."""
    out = artifact_dir()
    py = Path(sys.executable).resolve().as_posix()
    harness = HARNESS.as_posix()
    out_posix = out.as_posix()
    text = "\n".join(
        [
            "[[gui.desktop]]",
            "desktop_id = 1",
            'driver = "flaui"',
            f'exe = "{py}"',
            f'args = "{harness} --role settings --title DemoSettings --out {out_posix}"',
            'title = "DemoSettings"',
            "timeout_s = 30",
            "",
            "[[gui.desktop]]",
            "desktop_id = 2",
            'driver = "flaui"',
            f'exe = "{py}"',
            (
                f'args = "{harness} --role fixture --title DemoFixture '
                f'--out {out_posix} --phrase zDemoShot"'
            ),
            'title = "DemoFixture"',
            "timeout_s = 30",
            "",
        ],
    )
    path.write_text(text, encoding="utf-8")
    return path
