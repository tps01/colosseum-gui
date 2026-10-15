# Desktop product suite (tiny harness)

Windows-only teaching suite: multi-`desktop_id`, launch `args=`, chord
`press_key`, and `col.shared.verify.verify_new_file` against side-effect files.

This is **not** OCR. The harness writes files; Colosseum waits for those files.

## Prerequisites

- Windows interactive desktop (keep the harness windows uncovered)
- `colosseum-core`, `colosseum-gui` **0.2.3+** (`args=` + chord keys), `colosseum-shared` **0.3.5+**

```powershell
pip install -e ../../colosseum-core -e ../.. -e ../../../colosseum-shared
# From the colosseum-gui repo root, with siblings checked out beside it.
```

## Run

```powershell
# From colosseum-gui repo root:
colosseum run-suite examples/desktop_suite/suite.toml -g examples/desktop_suite/config.toml
```

## What it shows

| Script | Pattern |
| --- | --- |
| `setup_config.py` | Placeholder `-g` file → rewrite absolute-path FlaUI TOML → `load_config` |
| `test_settings_save.py` | Launch `args=` + `press_key` → `verify_new_file` |
| `test_fixture_hotkey.py` | Auto capture file + chord `ctrl+shift+p` → another file |

(The harness is Tk for zero-build setup. Prefer real WPF/WinForms AutomationId
clicks for product UIs — see Notepad / pay_attention suites.)
| `teardown_close.py` | `close_all()` for apps Colosseum launched |

Background / windowless product processes are **not** FlaUI desktops: launch them
with `subprocess` (or your own helper), track PIDs, and kill in teardown. See
the gui plugin README section *Desktop product suites*.
