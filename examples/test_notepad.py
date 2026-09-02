"""Launch inbox Notepad with ``col.gui.desktop`` (FlaUI / UIA3).

FlaUI's README launches ``notepad.exe``. On Windows 11 that exe is a stub: it
exits and the real editor is another process, so this example also sets
``title = "Notepad"`` and the driver attaches to that window. Windows 10
Notepad is classic Win32 (Edit); Windows 11 is WinUI (Document).
``role="edit"`` matches both. Calculator and Task Manager are poor targets
(Store app / elevation).

Windows only. Run from the plugin repo::

    colosseum run examples/test_notepad.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import colosseum as col

_WINDOWS_ONLY = "This example requires Windows (inbox Notepad and driver=flaui)."


def _write_config() -> Path:
    path = Path(tempfile.gettempdir()) / "colosseum_gui_notepad_example.toml"
    path.write_text(
        "\n".join(
            [
                "[[gui.desktop]]",
                "desktop_id = 1",
                'driver = "flaui"',
                'exe = "notepad.exe"',
                'title = "Notepad"',
                "timeout_s = 30",
                "",
            ],
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    if not sys.platform.startswith("win"):
        raise OSError(_WINDOWS_ONLY)
    col.config.load_config(str(_write_config()))
    col.gui.desktop.connect(desktop_id=1)
    col.gui.desktop.wait_stable(desktop_id=1, timeout_s=5.0)
    col.gui.desktop.verify_visible(desktop_id=1, key="editor", role="edit")
    col.gui.desktop.type_text(
        desktop_id=1, text="colosseum notepad", role="edit", input="keys",
    )
    col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/notepad.png")
    col.gui.desktop.capture_tree(desktop_id=1, path="captures/notepad_tree.json")


if __name__ == "__main__":
    main()
    col.endex()
