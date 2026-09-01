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

That single package install includes Playwright, desktop drivers (FlaUI + bundled
UIA DLLs on Windows; python-xlib on Linux; mss), and test/static tooling. On bare
Ubuntu, also run `playwright install-deps` when using headed Chromium.

## Kind x driver matrix

| Kind | Driver | Platforms | Notes |
| --- | --- | --- | --- |
| `gui.web` | `sim` | any | CI / unit tests |
| `gui.web` | `playwright` | Linux, Windows | Role/CSS locators, nav timing |
| `gui.desktop` | `sim` | any | CI / unit tests |
| `gui.desktop` | `generic` | Linux, Windows | Screenshot, image/coord click |
| `gui.desktop` | `flaui` | Windows only | UIA3 via pythonnet; XPath; image/coord |

`driver=generic` on Linux is the X11 / X11-forwarded path. AT-SPI is not
forwarded over `ssh -X`; use image or coordinates, not UIA-style locators.

On Windows, `driver=flaui` is the default and combines UIA locators with
screenshot and image matching in one backend. `driver=pywinauto` is accepted as a
deprecated alias for `flaui`.

## Config TOML

```toml
[[gui.web]]
web_id = 1
driver = "sim"            # or playwright
url = "http://127.0.0.1:8080"

[[gui.desktop]]
desktop_id = 1
driver = "sim"            # or generic | flaui
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
col.gui.desktop.click(desktop_id=1, xpath="//Button[@AutomationId='StartBtn']")
col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/desk.png")
col.endex()
```

Use `import colosseum as col`. Do not `from colosseum.gui import ...` (that is
the core runner package).

Driver-backed ops (for example `automation_id=` on desktop, or tree waits on
web) raise `GuiCapabilityError` when the configured driver cannot perform them.
When a capability error occurs, drivers that expose `capture_tree` also write
`captures/capability_debug_tree.json` under the run output directory.

Generic desktop click is best-effort and may miss on DPI or focus - same idea as
generic SCPI on equipment.

## FlaUI vendor DLLs

Windows desktop automation loads vendored FlaUI 4.0.0 assemblies from
`colosseum_gui/vendor/flaui/` (MIT; see `FlaUI-LICENSE.txt`). Refresh them with:

```bash
python scripts/vendor_flaui_dlls.py
```

## Develop

```bash
pip install -e ../colosseum-core
pip install -e .
pytest
ruff check colosseum_gui
mypy
```

On Windows, validate the FlaUI bridge against a real app:

```bash
python scripts/spike_flaui.py
```
