Visual evidence and timing
==========================

Run the self-contained sim example from this repository root::

   colosseum run examples/visual_checks.py -g examples/configs/config.gui.sim.toml

No browser, display server or product application is used. The committed
``sim_blue.png`` is a fixed 64 x 48 expected image, and ``contrast.png`` has known
black/white regions. These fixtures are independent of the screenshots captured
during the run. Expected: PASS, two timing measurements, a contrast measurement
of 21, screenshot PNG plus ``.png.meta.json``, and tree JSON under ``captures/``.

.. literalinclude:: ../../../../examples/visual_checks.py
   :language: python

On a real product, capture a candidate screenshot, review it, then commit it as
the expected baseline. A test must compare against that reviewed image; copying
the current screenshot over the baseline inside the test defeats the check.
Baseline paths are CWD-relative or absolute. Actual screenshot paths can resolve
under the active run directory. Equal image dimensions are required; a mismatch
is ERROR. Pixel differences above ``threshold`` count toward ``max_diff_ratio``.
A failed comparison attempts to save an ``*_diff.png`` beside the actual image.

Keep viewport/window size, display scaling, theme, font rendering and browser
version consistent. Screenshot coordinates are image pixels; use the metadata
sidecar to check dimensions and DPI before choosing foreground/background boxes.
Sample flat areas inside glyph/background regions: averaging antialiased edges
changes the contrast result. The synthetic contrast example demonstrates the
calculation, not a complete accessibility assessment of a product screen.

``measure_action_latency_ms`` performs the click and measures until that call
returns. It does not wait for a business operation to finish. Follow it with an
explicit ``wait`` for the resulting product state. ``measure_navigation_ms``
reads the backend's last navigation duration. Use distinct evidence keys.

Web and desktop offer the same file-based visual operations, but locator/tree
support depends on the backend. Desktop ``generic`` supports image/coordinates/
keys; UIA tree/visible/text/enabled checks require FlaUI or desktop sim. Preserve
window focus and position for coordinate/image procedures. See :doc:`getting_started`.

Screenshots, trees and sidecars are saved files, without measurement artifact
index rows. Capture requires artifacts enabled. Verification-only can compare
explicit existing image files; live visible/text/enabled verifiers still open a
backend. A previous database alone cannot reconstruct a product UI.
