"""Tiny Tk harness for the desktop_suite example (Windows / interactive).

Roles:
  settings — window with a Save button; writes ``saved.ok`` under ``--out``
  fixture  — labeled pane; writes ``phrase_screenshot.txt`` after a short delay;
             Ctrl+Shift+P writes ``hotkey.ok``
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path


def _write(out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_text("ok\n", encoding="utf-8")


def _run_settings(*, title: str, out: Path) -> None:
    # Tk buttons are awkward under UIA; Save is triggered by pressing "s"
    # (FlaUI press_key) so the suite stays reliable without a compiled GUI.
    root = tk.Tk()
    root.title(title)
    root.geometry("360x160+40+40")
    tk.Label(root, text="Demo settings — press S to save").pack(pady=24)

    def on_save(_event: object = None) -> None:
        _write(out, "saved.ok")

    root.bind("<s>", on_save)
    root.bind("<S>", on_save)
    root.focus_force()
    root.mainloop()


def _run_fixture(*, title: str, out: Path, phrase: str) -> None:
    root = tk.Tk()
    root.title(title)
    root.geometry("420x220+40+40")
    tk.Label(root, text=phrase, font=("Segoe UI", 18)).pack(expand=True)

    def on_hotkey(_event: object = None) -> None:
        _write(out, "hotkey.ok")

    root.bind("<Control-Shift-P>", on_hotkey)
    root.after(800, lambda: _write(out, f"{phrase}_screenshot.txt"))
    root.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("settings", "fixture"), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--phrase", default="zDemoShot")
    args = parser.parse_args(argv)
    if args.role == "settings":
        _run_settings(title=args.title, out=args.out)
    else:
        _run_fixture(title=args.title, out=args.out, phrase=args.phrase)
    return 0


if __name__ == "__main__":
    sys.exit(main())
