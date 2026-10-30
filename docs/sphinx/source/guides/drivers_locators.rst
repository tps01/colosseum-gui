Choosing drivers and reliable locators
======================================

The **desktop runner** (``colosseum --gui``) launches and monitors Colosseum
tests. The **GUI automation plugin** (``col.gui.web`` / ``col.gui.desktop``)
interacts with the application under test.

Choose a driver
---------------

.. list-table::
   :header-rows: 1

   * - Target
     - Driver
     - Capabilities and limits
   * - Offline web or desktop procedure
     - ``sim``
     - Fixtures; web locators for web, UIA-style locators for desktop.
   * - Real browser
     - ``playwright``
     - Roles, accessible names, test IDs, CSS, XPath; Windows/Linux.
   * - Windows application with an accessibility tree
     - ``flaui`` (Windows desktop default)
     - UIA automation IDs, roles, XPath, tree checks, images/coordinates.
   * - Image/coordinate desktop automation
     - ``generic``
     - Windows or Linux X11/XWayland; images, coordinates, and keys.
       No UIA text/visible/enabled/tree operations.

Choose the target kind first, then its driver. Passing web ``css`` or
``test_id`` to desktop, or desktop ``automation_id`` to web, is invalid.
A sim desktop test using UIA operations cannot run unchanged on ``generic``.

Platform setup
--------------

Install the GUI wheel alongside core. For Playwright, run
``playwright install chromium``; on bare Ubuntu, install its system browser
dependencies with ``playwright install-deps``. Real desktop tests need an
interactive, unlocked session with access to the application. Linux generic
needs X11/XWayland; SSH X forwarding does not forward an accessibility tree.
On Windows, automation and the application need compatible privilege levels.
Use the Notepad example before attempting an elevated or custom-rendered app.

Start from the configuration and exact repository commands in
:doc:`getting_started` and :doc:`/config_reference`.

Choose a locator
----------------

Inside a configured ``main()`` with a matching live application::

   col.gui.web.click(web_id=1, role="button", name="Save")
   col.gui.web.click(web_id=1, test_id="save-button")
   col.gui.web.click(web_id=1, css="button[data-action='save']")
   col.gui.desktop.click(desktop_id=1, automation_id="SaveButton")
   col.gui.desktop.click(desktop_id=1, xpath="//Button[@AutomationId='SaveButton']")

These are alternative locators for different applications, not a sequence to
copy blindly. Prefer a stable accessible role/name or a product-owned test ID
on web, and an automation ID on FlaUI. CSS is useful for stable attributes;
avoid generated classes and element positions. XPath works when no stable ID
exists, but long paths tied to layout are fragile. Confirm locator uniqueness
from the actual page or accessibility tree, especially for repeated rows.

For custom-rendered controls without accessible identifiers, use reviewed image
templates or coordinates as a fallback on desktop. Keep the window position,
size, focus, theme, and display scaling consistent. Coordinates refer to the
driver's input surface; screenshot pixels and scaled desktop coordinates can
differ. Check screenshot metadata before selecting points or comparison boxes.

Wait for application state
--------------------------

Use the supported tree-based ``wait`` operations on Playwright/FlaUI rather
than a fixed sleep when waiting for a control or state. See :doc:`/api/web`
and :doc:`/api/desktop` for exact selectors and timeouts. A click returning
does not prove a background business operation finished. Wait for its visible
state or verify a file/service side effect separately. Generic desktop cannot
provide UIA waits; use an observable side effect or qualified image strategy.

Diagnose a missing element
--------------------------

Capture a screenshot and, on a tree-capable driver, ``capture_tree``. Confirm
the correct page/window is active, the identifier exists, the locator is
supported by that driver, and focus is on the intended target. Capability errors
attempt to write ``captures/capability_debug_tree.json`` on drivers that expose
trees. An inaccessible or custom-drawn control may need an image-based path.
See :doc:`visual_workflows` for screenshot baselines, DPI, and timing limits.

Bridge/runtime details for maintainers are in :doc:`development`.
