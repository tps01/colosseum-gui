# Colosseum GUI

## Documentation

API reference (GitHub Pages): https://tps01.github.io/colosseum-gui/

Framework hub: https://tps01.github.io/colosseum-core/

First-party Colosseum plugin for **product UI automation** (`col.gui.web` /
`col.gui.desktop`). This is not the core test-runner UI (`colosseum --gui`).

Web and desktop are separate kinds, like `col.equipment.speca` vs
`col.equipment.oscope`. Drivers implement each kind.

## Install

Download the wheel from [GitHub Releases](https://github.com/tps01/colosseum-gui/releases)
and install it in the same environment as core. Replace `<version>` with
the downloaded filename. For development, use `python -m pip install -e .`.

```bash
python -m pip install "./colosseum_gui-<version>-py3-none-any.whl"
playwright install chromium
```

This requires `colosseum-core` `>=0.17.0,<0.18` and registers the `gui` namespace through
the `colosseum.plugins` entry point.

That single package install includes Playwright, desktop drivers (FlaUI + bundled
UIA DLLs on Windows; python-xlib on Linux; mss), and test/static tooling. On bare
Ubuntu, also run `playwright install-deps` when using headed Chromium.

## Kind x driver matrix

| Kind | Driver | Platforms | Notes |
| --- | --- | --- | --- |
| `gui.web` | `sim` | any | CI / unit tests (web locators only) |
| `gui.web` | `playwright` | Linux, Windows | Role/CSS/`test_id`; `select_option`; nav timing |
| `gui.desktop` | `sim` | any | CI stand-in for the **UIA** desktop surface |
| `gui.desktop` | `flaui` | Windows (default) | UIA3: `automation_id` / role / XPath; image/coord |
| `gui.desktop` | `generic` | Linux, Windows | Image / coordinates / keys only — **not** UIA |

Locators are kind-honest: `col.gui.web` does not take `automation_id`;
`col.gui.desktop` does not take `css` / `test_id`. Use the matching namespace.

**Desktop capability:** treat FlaUI (and desktop `sim`) as the UIA contract —
`verify_text` / `verify_visible` / `verify_enabled` / tree `wait` need that path.
`driver=generic` is the image/coords/keys fallback (Linux X11 / XWayland, or when
you are not using UIA). It raises `GuiCapabilityError` for UIA-only calls; do not
write suites against `sim` and expect them to run on `generic` without changes.

`driver=generic` on Linux is the X11 / X11-forwarded path. AT-SPI is not
forwarded over `ssh -X`; use image or coordinates, not UIA-style locators.

On Windows, `driver=flaui` is the default (UIA3, which FlaUI recommends for
WPF and Store-style apps; classic Win32 still works). Screenshots use mss so
pythonnet does not depend on `System.Drawing`. The bridge pins
`PYTHONNET_RUNTIME=netfx` so a machine with the .NET SDK does not silently
switch to CoreCLR.

Do not use Calculator (FlaUI documents that `calc.exe` is the pre-Windows 8
app only) or Task Manager (often elevated; UIA from a normal Python process
cannot see it). Inbox Notepad is the portable target.

## Config TOML

```toml
[gui.web]
web_id = 1
driver = "sim"            # or playwright
url = "http://127.0.0.1:8080"

[gui.desktop]
desktop_id = 1
driver = "sim"            # or generic | flaui
title = "Radio Control"
# exe = "C:/apps/tool.exe"
# args = "fixture --phrase TOKEN --title Pane"   # or a string array
```

## Usage

```python
import colosseum as col

col.config.load_config("examples/configs/config.gui.sim.toml")
col.gui.web.navigate(web_id=1, url="http://dut/")
col.gui.web.click(web_id=1, role="button", name="Start")
col.gui.web.select_option(web_id=1, test_id="sku", value="Sprocket-7")
col.gui.web.capture_screenshot(web_id=1, path="captures/after.png")

col.gui.desktop.click(desktop_id=1, image="goldens/start.png")
col.gui.desktop.click(desktop_id=1, xpath="//Button[@AutomationId='StartBtn']")
col.gui.desktop.press_key(desktop_id=1, key="ctrl+shift+p")
col.gui.desktop.capture_screenshot(desktop_id=1, path="captures/desk.png")
col.endex()
```

Use `import colosseum as col`. Do not `from colosseum.gui import ...` (that is
the core runner package).

## Desktop product suites

`colosseum --gui` is the **operator** runner UI (core). `col.gui.desktop` drives
the **product under test**. Do not confuse the two.

For a real Windows `.exe` (or a small harness) with multiple windows:

1. Keep a **placeholder** `-g` TOML in the suite so CLI has a path before setup.
2. In suite setup, write a real `gui.toml` with absolute `exe` / `args` / `title`,
   then `col.config.load_config(..., force=True)` again (CLI `-g` is pinned;
   without `force=True` the reload is ignored).
3. Use one `[gui.desktop]` row per **windowed** process Colosseum should launch
   and attach to (`driver = "flaui"`, launch `args=` supported in gui **0.2.3+** /
   kind-honest locators in **0.3.0+**; use `[[gui.desktop]]` when the file has
   more than one desktop row).
4. Prove async product work with **side-effect files**
   (`col.shared.verify.snapshot_files` / `verify_new_file` / `verify_no_new_file`),
   not by re-implementing OCR inside Colosseum.
5. **Background / windowless** processes (no UI to attach): start with
   `subprocess`, keep the `Popen` handle, terminate in teardown. FlaUI
   `close_all()` only kills apps this plugin launched as desktop sessions.
6. Run on an **interactive** desktop session; leave fixture windows uncovered
   (locked / remote sessions without a desktop will flake).

Teaching suite (tiny Tk harness, multi-desktop, hotkey, file wait):

```bash
pip install -e ../colosseum-shared   # 0.3.5+ for verify_new_file
colosseum run-suite examples/desktop_suite/suite.toml -g examples/desktop_suite/config.toml
```

See `examples/desktop_suite/README.md`.

## Examples

Sim smoke (no display, no browser):

```bash
colosseum run examples/smoke_test.py -g examples/configs/config.gui.sim.toml
```

Live webpage on localhost (serves the widget-factory site in
``examples/test_webpage/``, Playwright):

```bash
playwright install chromium
colosseum run examples/test_webpage.py -g examples/test_webpage/config.toml
```

Live inbox **Notepad** on Windows (FlaUI's own sample app; UIA3). No extra
install beyond the plugin:

```bash
colosseum run examples/test_notepad.py
```

Live core runner UI as a **child** process (does not drive the window you
launched the test from). Windows attaches by `process_id` (FlaUI). CustomTkinter
does not expose native UIA button ids, so this example screenshots and dumps
the tree rather than clicking. Prefer the Notepad example for a portable
desktop smoke. Run from a terminal:

```bash
colosseum run examples/test_runner_gui.py
```

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
