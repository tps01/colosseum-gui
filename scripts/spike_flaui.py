#!/usr/bin/env python3
"""Windows-only spike: launch inbox Notepad via the FlaUI bridge."""

from __future__ import annotations

import sys


def main() -> int:
    if not sys.platform.startswith("win"):
        print("spike_flaui.py requires Windows")
        return 1

    from colosseum_gui.backends.desktop.flaui_driver import FlaUIDesktopBackend

    backend = FlaUIDesktopBackend(
        desktop_id=99,
        config={"exe": "notepad.exe", "title": "Notepad", "timeout_s": 15.0},
    )
    try:
        tree = backend.capture_tree()
        print(f"captured tree with {len(tree.get('controls', []))} nodes")
        backend.type_text(text="FlaUI spike", role="edit", input="keys")
    finally:
        backend.close()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
