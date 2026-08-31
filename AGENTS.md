# Agent guide

Read `RULES.md` before changing dependencies. Do not commit, push, merge, or tag
unless
the user explicitly requests it.

## Scope

`colosseum-gui` is a first-party Colosseum plugin for **product UI automation**:

- Registers the `gui` namespace → `col.gui.web.*` and `col.gui.desktop.*`
- Web and desktop are separate kinds (like `speca` vs `oscope`)
- Drivers implement each kind (`sim`, `playwright`, `generic`, `pywinauto`)
- Declares all runtime, driver, and test/static deps in main `dependencies`
  (one `pip install` / `pip install -e .`; see `RULES.md`)

Core's `colosseum.gui` package is the optional **test-runner UI** (`colosseum
--gui`).
Test scripts must use `import colosseum as col` and `col.gui.web` /
`col.gui.desktop`,
and must not `from colosseum.gui import ...`.

## Change discipline

Prefer focused, compact changes. Do not commit unless asked. Read `RULES.md` at
task start.

## Footprint

Follow the workspace **Minimizing footprint** section (top-level `AGENTS.md`).
Inventory
existing code before adding files; prefer merge, relocate, or delete over new
modules.
Keep plugin-only helpers local (e.g. `_paths.py`, `_cache.py`). Do not expand
core for
single-plugin needs.

## Workflow

When completing changes, increment the package version in `pyproject.toml` using
semantic
versioning. Agents cannot increment the major number.

When finishing a development session: `python scripts/cleanup.py --dry-run`,
then
`python scripts/cleanup.py` if the list looks right. See workspace `AGENTS.md`
(**Simulated annealing**, **End-of-development cleanup**).
