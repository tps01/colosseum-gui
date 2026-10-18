Getting started
===============

Install the ``colosseum-gui`` wheel into the same virtual environment as
``colosseum-core``. This plugin drives **product** UI (``col.gui.web`` /
``col.gui.desktop``). It is not the operator runner (``colosseum --gui``).

1. Config
---------

Sim TOML (see ``examples/configs/config.gui.sim.toml``)::

   [gui.web]
   web_id = 1
   driver = "sim"
   url = "http://127.0.0.1:8080"

   [gui.desktop]
   desktop_id = 1
   driver = "sim"
   title = "SimWindow"

Live desktop rows often set ``exe``, ``args``, and a window ``title``. Web rows
set ``url`` and a browser ``driver``. Prefer the matching namespace for locators
(web: ``css`` / ``test_id`` / ``role``; desktop: ``automation_id`` / ``xpath`` /
image).

2. Procedure + verification
---------------------------

Web::

   import colosseum as col

   def main() -> None:
       col.gui.web.navigate(web_id=1, url="http://127.0.0.1:8080")
       col.gui.web.click(web_id=1, role="button", name="Start")
       col.gui.web.verify_visible(web_id=1, test_id="status", key="status_visible")

Desktop and file side-effects often pair with ``col.shared.verify_*`` (install
``colosseum-shared``). A fuller multi-app recipe is
``examples/desktop_suite/`` in this repository.

3. Run
------

::

   colosseum run ui_smoke.py -g config.gui.sim.toml

Copy-out GUI stubs: ``gui/`` in
`colosseum-library <https://github.com/tps01/colosseum-library>`__.
Framework docs: `core hub <https://tps01.github.io/colosseum-core/>`__.
