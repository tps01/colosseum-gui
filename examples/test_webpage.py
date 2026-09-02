"""Drive the widget-factory page under ``test_webpage/`` with ``col.gui.web``.

Walks catalog (native ``<select>`` + queue), home start production (slow lot draw), and
shop-floor inspect (slow grade). Locators use ``data-testid``; status live
regions do not expose inner text as an accessible name.

Requires ``playwright install chromium``. Run from the plugin repo::

    colosseum run examples/test_webpage.py -g examples/test_webpage/config.toml
"""

from __future__ import annotations

import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import colosseum as col

_PAGE = Path(__file__).resolve().parent / "test_webpage"
_WEB = 1
_SLOW_S = 10.0


def _serve_page() -> tuple[ThreadingHTTPServer, str]:
    handler = partial(SimpleHTTPRequestHandler, directory=str(_PAGE))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    return httpd, f"http://{host}:{port}/"


def _queue_sprocket() -> None:
    col.gui.web.click(web_id=_WEB, test_id="nav-catalog")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="widget-select")
    col.gui.web.select_option(web_id=_WEB, test_id="widget-select", value="Sprocket-7")
    col.gui.web.click(web_id=_WEB, test_id="queue-btn")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="queue-note")
    col.gui.web.verify_text(
        web_id=_WEB,
        key="queue_note",
        expected="Queued Sprocket-7 for the next shift.",
        test_id="queue-note",
    )
    col.gui.web.capture_screenshot(web_id=_WEB, path="captures/catalog_queued.png")


def _start_production() -> None:
    col.gui.web.click(web_id=_WEB, test_id="nav-home")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="start-btn")
    col.gui.web.verify_enabled(web_id=_WEB, key="start_ready", test_id="start-btn")
    col.gui.web.click(web_id=_WEB, test_id="start-btn")
    col.gui.web.wait(
        web_id=_WEB, until="visible", test_id="run-status", timeout_s=_SLOW_S,
    )
    col.gui.web.verify_text(
        web_id=_WEB, key="status_text", expected="Running", test_id="run-status",
    )
    col.gui.web.wait(
        web_id=_WEB, until="text", test_id="lot-number", text="Sprocket-7",
        timeout_s=_SLOW_S,
    )
    col.gui.web.verify_visible(web_id=_WEB, key="lot", test_id="lot-number")
    col.gui.web.verify_enabled(web_id=_WEB, key="start_idle", test_id="start-btn")
    col.gui.web.capture_screenshot(web_id=_WEB, path="captures/home_running.png")


def _inspect_lot() -> None:
    col.gui.web.click(web_id=_WEB, test_id="nav-floor")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="inspect-btn")
    col.gui.web.click(web_id=_WEB, test_id="inspect-btn")
    col.gui.web.wait(
        web_id=_WEB, until="visible", test_id="inspect-result", timeout_s=_SLOW_S,
    )
    col.gui.web.wait(
        web_id=_WEB, until="text", test_id="inspect-result", text="Grade",
        timeout_s=_SLOW_S,
    )
    col.gui.web.verify_visible(web_id=_WEB, key="grade", test_id="inspect-result")
    col.gui.web.capture_screenshot(web_id=_WEB, path="captures/floor_inspected.png")


def _open_lead_times() -> None:
    col.gui.web.click(web_id=_WEB, test_id="nav-home")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="lead-times")
    col.gui.web.click(web_id=_WEB, test_id="lead-times")
    col.gui.web.wait(web_id=_WEB, until="visible", test_id="lead-times-body")
    col.gui.web.wait(
        web_id=_WEB, until="text", test_id="lead-times-body", text="16:30",
    )


def main() -> None:
    col.config.load_config(str(_PAGE / "config.toml"))
    httpd, url = _serve_page()
    try:
        col.gui.web.connect(web_id=_WEB)
        col.gui.web.navigate(web_id=_WEB, url=url)
        col.gui.web.measure_navigation_ms(web_id=_WEB, key="home_nav_ms")
        col.gui.web.verify_visible(web_id=_WEB, key="start_btn", test_id="start-btn")
        _queue_sprocket()
        _start_production()
        _inspect_lot()
        _open_lead_times()
        col.gui.web.capture_tree(web_id=_WEB, path="captures/widget_factory_tree.json")
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
    col.endex()
