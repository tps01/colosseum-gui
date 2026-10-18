"""Offline screenshot, tree, visual-baseline, contrast and timing example.

    colosseum run examples/visual_checks.py -g examples/configs/config.gui.sim.toml

Uses fixed synthetic PNG fixtures. These checks teach the evidence flow; they
do not establish a real product's appearance, accessibility or response time.
"""

from pathlib import Path

import colosseum as col


def main() -> None:
    examples = Path(__file__).resolve().parent
    col.config.load_config(str(examples / "configs/config.gui.sim.toml"))
    col.gui.web.navigate(web_id=1, url="http://example.test/start")
    col.gui.web.measure_navigation_ms(web_id=1, key="navigation")
    col.gui.web.measure_action_latency_ms(web_id=1, key="click_return", role="button", name="Start")
    col.gui.web.wait(web_id=1, until="visible", role="status", name="Running", timeout_s=1.0)
    col.gui.web.verify_visible(web_id=1, key="running", role="status", name="Running")
    col.gui.web.capture_screenshot(web_id=1, path="captures/actual.png")
    col.gui.web.capture_tree(web_id=1, path="captures/tree.json")
    col.gui.web.verify_visual(
        key="appearance", path="captures/actual.png",
        baseline=str(examples / "fixtures/sim_blue.png"), max_diff_ratio=0.0, threshold=0,
    )
    # Known black and white regions in an independent synthetic image: ratio 21.
    col.gui.web.measure_contrast_ratio(
        web_id=1, key="contrast", path=str(examples / "fixtures/contrast.png"),
        fg_x=0, fg_y=0, fg_w=8, fg_h=8, bg_x=16, bg_y=0, bg_w=8, bg_h=8,
    )
    col.gui.web.verify_contrast(key="contrast", minimum=4.5)


if __name__ == "__main__":
    main()
    col.endex()
