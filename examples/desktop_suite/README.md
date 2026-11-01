# Desktop product suite (tiny harness)

Windows-only teaching suite: multi-`desktop_id`, launch `args=`, chord
`press_key`, and `col.shared.verify.verify_new_file` against side-effect files.

This is **not** OCR. The harness writes files; Colosseum waits for those files.

## Prerequisites

- Windows interactive desktop (keep the harness windows uncovered)
- Compatible core, GUI and shared wheels. Current plugin manifests require
  `colosseum-core>=0.18,<0.19`; package version numbers are independent.

```powershell
# Download compatible release wheels; replace the version placeholders.
python -m pip install `
  "./colosseum_core-<core-version>-py3-none-any.whl" `
  "./colosseum_gui-<gui-version>-py3-none-any.whl" `
  "./colosseum_shared-<shared-version>-py3-none-any.whl"
```

## Run

```powershell
# From colosseum-gui repo root:
colosseum run-suite examples/desktop_suite/suite.toml -g examples/desktop_suite/config.toml
```

## What it shows

| Script | Pattern |
| --- | --- |
| `setup_config.py` | Placeholder `-g` file → rewrite absolute-path FlaUI TOML → `load_config(..., force=True)` |
| `test_settings_save.py` | Launch `args=` + `press_key` → `verify_new_file` |
| `test_fixture_hotkey.py` | Auto capture file + chord `ctrl+shift+p` → another file |

(The harness is Tk for zero-build setup. Prefer real WPF/WinForms AutomationId
clicks for product UIs — see Notepad / pay_attention suites.)
| `teardown_close.py` | `close_all()` for apps Colosseum launched |

Background / windowless product processes are **not** FlaUI desktops: launch them
with `subprocess` (or your own helper), track PIDs, and kill in teardown. See
the gui plugin README section *Desktop product suites*.
