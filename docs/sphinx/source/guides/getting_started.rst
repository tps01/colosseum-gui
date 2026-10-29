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

The following complete script exercises web and desktop sim backends:

.. literalinclude:: ../../../../examples/smoke_test.py
   :language: python

Desktop and file side-effects often pair with ``col.shared.verify.*`` (install
``colosseum-shared``). A fuller multi-app recipe is
``examples/desktop_suite/`` in this repository.

3. Run from the repository root
-------------------------------

::

   colosseum run examples/smoke_test.py -g examples/configs/config.gui.sim.toml

Copy-out GUI stubs: ``gui/`` in
`colosseum-library <https://github.com/tps01/colosseum-library>`__.
Framework docs: `core hub <https://tps01.github.io/colosseum-core/>`__.

The included files have this layout::

   examples/
     smoke_test.py
     configs/
       config.gui.sim.toml

The script resolves its config relative to ``__file__``. CLI ``-g`` pins the
chosen configuration, so that script load is ignored when the flag is present.
Use ``force=True`` only for an intentional replacement; see the
`core configuration guide <https://tps01.github.io/colosseum-core/guides/configuration.html>`__.
Expected: exit 0, required PASS checks for ``status`` and ``btn``, plus captured
web/desktop screenshots under the run's ``captures/`` directory. Simulated
results validate procedure flow, not the behavior of a real application.

For live setup, locator selection, and flaky-test diagnostics, see
:doc:`drivers_locators`. For image and timing evidence, see :doc:`visual_workflows`.
