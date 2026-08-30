# Colosseum GUI

First-party Colosseum plugin for **product UI automation** (`col.gui.web` /
`col.gui.desktop`). This is not the core test-runner UI (`colosseum --gui`).

Web and desktop are separate kinds, like `col.equipment.speca` vs
`col.equipment.oscope`. Drivers implement each kind.

## Install

```bash
pip install colosseum-gui
playwright install chromium
```

This requires `colosseum-core` 0.16.1+ and registers the `gui` namespace through
the `colosseum.plugins` entry point.

That single package install includes Playwright, desktop drivers (pywinauto on
Windows; python-xlib on Linux; mss), and test/static tooling. On bare Ubuntu,
also run `playwright install-deps` when using headed Chromium.

## Kind x driver matrix

| Kind | Driver | Platforms | Notes |
| --- | --- | --- | --- |
| `gui.web` | `sim` | any | CI / unit tests |
| `gui.web` | `playwright` | Linux, Windows | Role/CSS locators, nav timing |
| `gui.desktop` | `sim` | any | CI / unit tests |
| `gui.desktop` | `generic` | Linux, Windows | Screenshot, image/coord click |
| `gui.desktop` | `pywinauto` | Windows only | UIA AutomationId / Invoke |

`driver=generic` on Linux is the X11 / X11-forwarded path. AT-SPI is not
forwarded over `ssh -X`; use image or coordinates, not UIA-style locators.

## Config TOML

```toml
[[gui.web]]
web_id = 1
driver = "sim"            # or playwright
url = "http://127.0.0.1:8080"

[[gui.desktop]]
desktop_id = 1
driver = "sim"            # or generic | pywinauto
title = "Radio Control"
```

## Usage

```python
import colosseum as col

col.config.load_config("examples/configs/config.gui.sim.toml")
col.gui.web.navigate(web_id=1, url="http://dut/")
col.gui.web.click(web_id=1, role="button", name="Start")
col.gui.web.capture_screenshot(web_id=1, path="captures/after.png")

col.gui.desktop.click(desktop_id=1, image="goldens/start.png")
col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/desk.png")
col.endex()
```

Use `import colosseum as col`. Do not `from colosseum.gui import ...` (that is
the core runner package).

Driver-backed ops (for example `automation_id=` on desktop, or tree waits on
web) raise `GuiCapabilityError` when the configured driver cannot perform them.
Generic desktop click is best-effort and may miss on DPI or focus - same idea as
generic SCPI on equipment.

## Expected artifacts

Normal CLI runs write `summary.json`, `summary.txt`, `execution.sqlite`, and
`debug.log` under the run output directory. When metadata is loaded (see
`examples/configs/metadata.yaml`), core also emits a WATS-format
`wats_<datetime>_<script>.json` report alongside those files.

## Develop

```bash
pip install -e ../colosseum-core
pip install -e .
pytest
ruff check colosseum_gui
mypy
```
