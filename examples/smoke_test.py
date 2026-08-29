"""Smoke example for col.gui.web / col.gui.desktop (sim drivers)."""

from __future__ import annotations

from pathlib import Path

import colosseum as col


def main() -> None:
    config = Path(__file__).with_name("configs") / "bench.gui.sim.toml"
    col.config.load_config(str(config))

    col.gui.web.navigate(web_id=1, url="http://example.test/start")
    col.gui.web.click(web_id=1, role="button", name="Start")
    col.gui.web.verify_visible(web_id=1, key="status", role="status", name="Running")
    col.gui.web.capture_screenshot(web_id=1, path="captures/web_after_start.png")

    col.gui.desktop.click(desktop_id=1, automation_id="StartBtn")
    col.gui.desktop.verify_text(
        desktop_id=1, key="btn", expected="Running", automation_id="StartBtn",
    )
    col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/desktop_after_start.png")


if __name__ == "__main__":
    main()
    col.endex()
