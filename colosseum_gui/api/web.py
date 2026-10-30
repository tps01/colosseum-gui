"""Web GUI APIs (``col.gui.web``)."""

from __future__ import annotations

import time

from colosseum.decorators import VerificationResult, command, measurement, verification

from colosseum_gui.api import _visual
from colosseum_gui.connections import get_web

__all__ = [
    "connect",
    "navigate",
    "click",
    "type_text",
    "select_option",
    "press_key",
    "hover",
    "wait",
    "wait_stable",
    "capture_screenshot",
    "capture_tree",
    "measure_navigation_ms",
    "measure_action_latency_ms",
    "measure_contrast_ratio",
    "verify_text",
    "verify_visible",
    "verify_enabled",
    "verify_visual",
    "verify_contrast",
]


@command
def connect(*, web_id: int) -> None:
    """Open (or reuse) a configured web surface.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int

    :returns: None

    :raises GuiConnectionError: Browser or sim backend could not be opened.
    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id)


@command
def navigate(*, web_id: int, url: str) -> None:
    """Navigate the web surface to ``url`` (Playwright / sim).

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param url: Absolute URL to open.
    :type url: str

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).navigate(url=url)


@command
def click(
    *,
    web_id: int,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    input: str | None = None,
) -> None:
    """Click an element (best-effort; role/CSS preferred on Playwright).

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param role: Accessible role (Playwright ``get_by_role``).
    :type role: str | None
    :param name: Accessible name.
    :type name: str | None
    :param test_id: ``data-testid`` value.
    :type test_id: str | None
    :param css: CSS selector.
    :type css: str | None
    :param xpath: XPath selector.
    :type xpath: str | None
    :param x: Page X for coordinate click.
    :type x: float | None
    :param y: Page Y for coordinate click.
    :type y: float | None
    :param input: ``invoke`` (default) or ``mouse``.
    :type input: str | None

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).click(
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
        input=input,
    )


@command
def type_text(
    *,
    web_id: int,
    text: str,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    input: str | None = None,
) -> None:
    """Type or fill text into an element.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param text: Text to enter.
    :type text: str
    :param role: Accessible role.
    :type role: str | None
    :param name: Accessible name.
    :type name: str | None
    :param test_id: ``data-testid`` value.
    :type test_id: str | None
    :param css: CSS selector.
    :type css: str | None
    :param xpath: XPath selector.
    :type xpath: str | None
    :param x: Page X for coordinate focus.
    :type x: float | None
    :param y: Page Y for coordinate focus.
    :type y: float | None
    :param input: Fill strategy hint.
    :type input: str | None

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).type_text(
        text=text,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
        input=input,
    )


@command
def select_option(
    *,
    web_id: int,
    value: str | None = None,
    label: str | None = None,
    index: int | None = None,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
) -> None:
    """Select an option on a native ``<select>`` (Playwright ``select_option``).

    Provide exactly one of ``value``, ``label``, or ``index``.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param value: Option ``value`` attribute.
    :type value: str | None
    :param label: Visible option label.
    :type label: str | None
    :param index: Zero-based option index.
    :type index: int | None
    :param role: Accessible role.
    :type role: str | None
    :param name: Accessible name.
    :type name: str | None
    :param test_id: ``data-testid`` value.
    :type test_id: str | None
    :param css: CSS selector.
    :type css: str | None
    :param xpath: XPath selector.
    :type xpath: str | None

    :returns: None

    :raises ValueError: None or more than one of ``value`` / ``label`` / ``index``.
    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).select_option(
        value=value,
        label=label,
        index=index,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
    )


@command
def press_key(*, web_id: int, key: str) -> None:
    """Press a key on the focused page.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Key name (for example ``Tab`` or ``Enter``).
    :type key: str

    :returns: None
    """
    get_web(web_id).press_key(key=key)


@command
def hover(
    *,
    web_id: int,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> None:
    """Hover an element.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).hover(
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
    )


@command
def wait(
    *,
    web_id: int,
    until: str,
    timeout_s: float = 10.0,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    text: str | None = None,
) -> None:
    """Wait until an element condition holds (Playwright / sim).

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param until: ``visible``, ``enabled``, or ``text``.
    :type until: str
    :param timeout_s: Timeout in seconds.
    :type timeout_s: float
    :param text: Expected text when ``until=text``.
    :type text: str | None

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).wait(
        until=until,
        timeout_s=timeout_s,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
        text=text,
    )


@command
def wait_stable(*, web_id: int, timeout_s: float = 2.0) -> None:
    """Wait until consecutive screenshots match (best-effort).

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param timeout_s: Maximum settle time.
    :type timeout_s: float

    :returns: None
    """
    get_web(web_id).wait_stable(timeout_s=timeout_s)


@command
def capture_screenshot(*, web_id: int, path: str) -> None:
    """Save a page screenshot under the active run output directory.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int

    Requires artifacts enabled. Screenshot/tree files and screenshot
    metadata sidecars are saved without measurement artifact-index rows.

    :param path: Path relative to the run output directory.
    :type path: str

    :returns: None
    """
    _visual.save_screenshot_artifact(get_web(web_id), path=path, kind="gui_web_screenshot")


@command
def capture_tree(*, web_id: int, path: str = "captures/web_tree.json") -> None:
    """Dump the accessibility tree (Playwright / sim) as a JSON artifact.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int

    Requires artifacts enabled. Screenshot/tree files and screenshot
    metadata sidecars are saved without measurement artifact-index rows.

    :param path: Path relative to the run output directory.
    :type path: str

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    _visual.save_tree_artifact(get_web(web_id), path=path, kind="gui_web_tree")


@measurement
def measure_navigation_ms(*, web_id: int, key: str) -> float:
    """Record the last navigation duration in milliseconds.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Unique measurement key within domain ``gui``.
    :type key: str

    :returns: Navigation time in milliseconds.
    :rtype: float
    """
    _ = key
    return float(get_web(web_id).measure_navigation_ms())


@measurement
def measure_action_latency_ms(
    *,
    web_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> float:
    """Click an element and measure wall time until the call returns.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Unique measurement key within domain ``gui``.
    :type key: str

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: Action latency in milliseconds.
    :rtype: float
    """
    _ = key
    backend = get_web(web_id)
    started = time.perf_counter()
    backend.click(role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y)
    return (time.perf_counter() - started) * 1000.0


@measurement
def measure_contrast_ratio(
    *,
    web_id: int,
    key: str,
    path: str,
    fg_x: int,
    fg_y: int,
    fg_w: int,
    fg_h: int,
    bg_x: int,
    bg_y: int,
    bg_w: int,
    bg_h: int,
) -> float:
    """Sample two rectangles from a prior screenshot and measure WCAG contrast.

    :param web_id: Unused for sampling (screenshot already captured); kept for kind symmetry.
    :type web_id: int
    :param key: Unique measurement key within domain ``gui``.
    :type key: str
    :param path: Screenshot path relative to the run output directory.
    :type path: str

    :param fg_x: Foreground sample rectangle left edge in screenshot pixels. The rectangle must
        fit inside the image; width and height must be positive.
    :param fg_y: Foreground sample rectangle top edge in screenshot pixels. The rectangle must
        fit inside the image; width and height must be positive.
    :param fg_w: Foreground sample rectangle width in screenshot pixels. The rectangle must fit
        inside the image; width and height must be positive.
    :param fg_h: Foreground sample rectangle height in screenshot pixels. The rectangle must fit
        inside the image; width and height must be positive.
    :param bg_x: Background sample rectangle left edge in screenshot pixels. The rectangle must
        fit inside the image; width and height must be positive.
    :param bg_y: Background sample rectangle top edge in screenshot pixels. The rectangle must
        fit inside the image; width and height must be positive.
    :param bg_w: Background sample rectangle width in screenshot pixels. The rectangle must fit
        inside the image; width and height must be positive.
    :param bg_h: Background sample rectangle height in screenshot pixels. The rectangle must fit
        inside the image; width and height must be positive.

    :returns: Contrast ratio.
    :rtype: float
    """
    _ = (web_id, key)
    return _visual.measure_contrast_ratio_from_path(
        path=path,
        fg_x=fg_x,
        fg_y=fg_y,
        fg_w=fg_w,
        fg_h=fg_h,
        bg_x=bg_x,
        bg_y=bg_y,
        bg_w=bg_w,
        bg_h=bg_h,
    )


@verification
def verify_text(
    *,
    web_id: int,
    key: str,
    expected: str,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify element text equals ``expected``.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Verification key.
    :type key: str
    :param expected: Expected text.
    :type expected: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: Pass/fail result.
    :rtype: VerificationResult

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    _ = key
    return _visual.verify_text_equals(
        get_web(web_id),
        expected=expected,
        optional=optional,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
    )


@verification
def verify_visible(
    *,
    web_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify an element is visible.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Verification key.
    :type key: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    return _visual.verify_is_visible(
        get_web(web_id),
        optional=optional,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
    )


@verification
def verify_enabled(
    *,
    web_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    test_id: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    x: float | None = None,
    y: float | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify an element is enabled.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
    :param key: Verification key.
    :type key: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :param role: Accessible role/control type; requires a tree-capable driver. None omits this
        selector.
    :param name: Accessible element name; None omits this selector. Prefer a stable, unique
        name.
    :param test_id: Web test identifier resolved by the browser backend; None omits this selector.
    :param css: Web CSS selector; None omits it. Prefer stable attributes over generated class
        names.
    :param xpath: XPath locator supported by the selected driver (web DOM or desktop UIA); None
        omits it.
    :param x: Horizontal input coordinate for the selected backend; None omits coordinate
        selection.
    :param y: Vertical input coordinate for the selected backend; None omits coordinate
        selection.

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    return _visual.verify_is_enabled(
        get_web(web_id),
        optional=optional,
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        x=x,
        y=y,
    )


@verification
def verify_visual(
    *,
    key: str,
    path: str,
    baseline: str,
    max_diff_ratio: float = 0.01,
    threshold: int = 16,
    optional: bool = False,
) -> VerificationResult:
    """Compare a web screenshot to a baseline PNG.

    :param key: Verification key.
    :type key: str
    :param path: Actual screenshot path.
    :type path: str
    :param baseline: Baseline PNG path.
    :type baseline: str
    :param max_diff_ratio: Maximum allowed differing-pixel fraction.
    :type max_diff_ratio: float
    :param threshold: Per-channel difference threshold.
    :type threshold: int
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    return _visual.verify_visual_paths(
        path=path,
        baseline=baseline,
        max_diff_ratio=max_diff_ratio,
        threshold=threshold,
        optional=optional,
    )


@verification
def verify_contrast(
    *,
    key: str,
    minimum: float = 4.5,
    optional: bool = False,
) -> VerificationResult:
    """Verify a prior ``measure_contrast_ratio`` meets ``minimum``.

    :param key: Measurement key shared with ``measure_contrast_ratio``.
    :type key: str
    :param minimum: Minimum contrast ratio.
    :type minimum: float
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    return _visual.verify_contrast_key(
        key=key,
        command_candidates=("web.measure_contrast_ratio",),
        minimum=minimum,
        optional=optional,
    )
