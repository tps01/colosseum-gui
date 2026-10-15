"""Desktop 1: launch-args settings pane; press S; wait for side-effect file."""

from __future__ import annotations

import colosseum as col
from support import artifact_dir


def main() -> None:
    out = artifact_dir()
    before = col.shared.verify.snapshot_files(str(out), pattern="saved.ok")
    col.gui.desktop.connect(desktop_id=1)
    col.gui.desktop.wait_stable(desktop_id=1, timeout_s=5.0)
    col.gui.desktop.press_key(desktop_id=1, key="s")
    col.shared.verify.verify_new_file(
        key="saved_ok",
        directory=str(out),
        before=before,
        pattern="saved.ok",
        timeout_s=10.0,
    )
    from colosseum_gui.connections import close_all

    close_all()


if __name__ == "__main__":
    main()
    col.endex()
