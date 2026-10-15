"""Drive a *child* ``colosseum --gui`` window, not the operator GUI.

Spawns the core runner UI as a subprocess, writes ``process_id`` into a temp
config, and attaches with ``col.gui.desktop``. On Windows that uses FlaUI attach
so a parent ``colosseum --gui`` (if you launched this test from it) is not the
target. CustomTkinter does not expose native UIA button ids, so this example
connects, dumps the tree, and screenshots rather than clicking CTk controls.

Run from a terminal (recommended)::

    colosseum run examples/test_runner_gui.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import colosseum as col

_STARTUP_WAIT_S = 3.0
_SHUTDOWN_WAIT_S = 5.0


def _spawn_runner() -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [sys.executable, "-c", "from colosseum.runner.cli import main; main(['--gui'])"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _write_desktop_config(process_id: int) -> Path:
    driver = "flaui" if sys.platform.startswith("win") else "generic"
    path = Path(tempfile.gettempdir()) / "colosseum_gui_runner_example.toml"
    path.write_text(
        "\n".join(
            [
                "[[gui.desktop]]",
                "desktop_id = 1",
                f'driver = "{driver}"',
                'title = "Colosseum"',
                f"process_id = {process_id}",
                "timeout_s = 30",
                "",
            ],
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    proc = _spawn_runner()
    try:
        time.sleep(_STARTUP_WAIT_S)
        col.config.load_config(str(_write_desktop_config(proc.pid)))
        col.gui.desktop.connect(desktop_id=1)
        col.gui.desktop.wait_stable(desktop_id=1, timeout_s=5.0)
        col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/runner_gui.png")
        col.gui.desktop.capture_tree(desktop_id=1, path="captures/runner_gui_tree.json")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=_SHUTDOWN_WAIT_S)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=_SHUTDOWN_WAIT_S)


if __name__ == "__main__":
    main()
    col.endex()
