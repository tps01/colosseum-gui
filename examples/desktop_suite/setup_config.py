"""Suite setup: write a real FlaUI gui.toml and point -g at it."""

from __future__ import annotations

import os
from pathlib import Path

import colosseum as col
from support import artifact_dir, write_gui_toml


def main() -> None:
    root = artifact_dir()
    os.environ["COLOSSEUM_DESKTOP_SUITE_OUT"] = str(root)
    for stale in root.glob("*"):
        if stale.is_file():
            stale.unlink()
    cfg = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))) / (
        "colosseum_desktop_suite_gui.toml"
    )
    write_gui_toml(cfg)
    col.config.load_config(str(cfg))


if __name__ == "__main__":
    main()
    col.endex()
