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
    image: str | None = None,
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
    :param image: Unused on web (desktop generic); reserved.
    :type image: str | None
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
        image=image,
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
    image: str | None = None,
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
    :param image: Unused on web.
    :type image: str | None
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
        image=image,
        x=x,
        y=y,
        input=input,
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
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> None:
    """Hover an element.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_web(web_id).hover(
        role=role,
        name=name,
        test_id=test_id,
        css=css,
        xpath=xpath,
        image=image,
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
    """Capture a page screenshot and register it as a run artifact.

    :param web_id: Configured ``gui.web`` id from bench TOML.
    :type web_id: int
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

    :returns: Pass/fail result.
    :rtype: VerificationResult

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    _ = key
    actual = get_web(web_id).get_text(
        role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
    )
    if actual == expected:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message=f"expected {expected!r}, got {actual!r}",
        optional=optional,
        actual=actual,
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

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    actual = get_web(web_id).is_visible(
        role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
    )
    if actual:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message="element is not visible",
        optional=optional,
        actual=actual,
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

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    actual = get_web(web_id).is_enabled(
        role=role, name=name, test_id=test_id, css=css, xpath=xpath, x=x, y=y
    )
    if actual:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message="element is not enabled",
        optional=optional,
        actual=actual,
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
