GUI driver implementation notes
===============================

On Windows, ``driver=flaui`` is the default (UIA3, which FlaUI recommends for
WPF and Store-style apps; classic Win32 still works). Screenshots use mss so
pythonnet does not depend on ``System.Drawing``. The bridge pins
``PYTHONNET_RUNTIME=netfx`` so a machine with the .NET SDK does not silently
switch to CoreCLR.


Run ``python -m pytest`` after driver changes. On an interactive Windows
desktop, ``python scripts/spike_flaui.py`` checks the real FlaUI bridge.
For test authors, see :doc:`drivers_locators`.
