Config reference
================

A config row is one TOML table. One window or page uses ``[gui.web]`` or
``[gui.desktop]``. Use ``[[gui.desktop]]`` only when the file shows two or more
rows of that same section. When the section is present, the integer id field
is required. No key on these sections is required. Comments come from the web
and desktop backend factories.

gui.web
-------

``open_web_backend`` defaults ``driver`` to ``playwright``. ``sim`` is the
other accepted driver.

.. code-block:: toml

   [gui.web]
   web_id = 1                          # required integer id
   driver = "playwright"               # optional; default playwright; sim or playwright
   url = "about:blank"                 # optional; default about:blank; launch path calls goto when it is not about:blank
   browser = "chromium"                # optional; default chromium; Playwright launcher name
   headed = false                      # optional; default false; true for 1, true, yes, or on
   cdp_url = "http://127.0.0.1:9222"   # optional; when set, chromium.connect_over_cdp instead of launching
   viewport = "1280x720"               # optional; WIDTHxHEIGHT when launching; omitted leaves the Playwright context unset
   timeout_s = 10                      # optional; seconds; default 10; stored as milliseconds

When ``cdp_url`` is set, the browser name is not used to launch. The first
existing browser context and page are reused. ``viewport`` is applied only on
a launched browser.

gui.desktop
-----------

``open_desktop_backend`` defaults ``driver`` to ``flaui`` on Windows and
``generic`` otherwise. ``x11`` and an empty driver select the generic backend.
``flaui`` raises ``OSError`` when the host is not Windows. FlaUI attach
requires ``exe``, ``process_id``, or ``title``.

.. code-block:: toml

   [gui.desktop]
   desktop_id = 1                      # required integer id
   driver = "flaui"                    # optional; default flaui on Windows, else generic; sim, generic, x11, or flaui
   title = ""                          # optional; default empty; window title or launch hint
   exe = "notepad.exe"                 # optional; flaui Application.Launch path
   args = ""                           # optional; string or list of launch arguments
   process_id = 4242                   # optional; flaui attaches to this PID when exe is absent
   timeout_s = 10                      # optional; seconds; default 10
   dpi_scale = 1.0                     # optional; default 1.0; recorded on capture metadata
   display = ":0"                      # optional; Linux generic/x11 display; falls back to DISPLAY

On Linux, the generic backend raises ``OSError`` when ``display`` and
``DISPLAY`` are both empty. Generic and FlaUI copy ``dpi_scale`` onto capture
metadata.
