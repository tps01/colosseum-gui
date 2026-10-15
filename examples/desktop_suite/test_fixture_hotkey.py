"""Desktop 2: fixture writes a capture file; Ctrl+Shift+P writes hotkey.ok."""

from __future__ import annotations

import colosseum as col

from support import artifact_dir


def main() -> None:
    out = artifact_dir()
    before_shot = col.shared.verify.snapshot_files(str(out), pattern="*_screenshot.txt")
    col.gui.desktop.connect(desktop_id=2)
    col.gui.desktop.wait_stable(desktop_id=2, timeout_s=5.0)
    col.shared.verify.verify_new_file(
        key="fixture_shot",
        directory=str(out),
        before=before_shot,
        pattern="*_screenshot.txt",
        timeout_s=10.0,
    )

    before_key = col.shared.verify.snapshot_files(str(out), pattern="hotkey.ok")
    col.gui.desktop.press_key(desktop_id=2, key="ctrl+shift+p")
    col.shared.verify.verify_new_file(
        key="hotkey_ok",
        directory=str(out),
        before=before_key,
        pattern="hotkey.ok",
        timeout_s=10.0,
    )

    from colosseum_gui.connections import close_all

    close_all()


if __name__ == "__main__":
    main()
    col.endex()
