"""Suite teardown: close FlaUI-owned harness windows."""

from __future__ import annotations

import colosseum as col


def main() -> None:
    try:
        from colosseum_gui.connections import close_all

        close_all()
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    main()
    col.endex()
