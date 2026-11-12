#!/usr/bin/env python3
"""Regression tests for screen-specific HUD visibility and lifecycle repair."""
from pathlib import Path
import subprocess, sys, tempfile

repo = Path(__file__).resolve().parents[1]
patcher = Path(__file__).with_name("apply_v6_screen_lifecycle_repair.py")
with tempfile.TemporaryDirectory(prefix="bz-screen-lifecycle-") as temp:
    root = Path(temp)
    html = root / "app/src/main/assets/www/index.html"
    html.parent.mkdir(parents=True)
    html.write_text("<!doctype html><html><head></head><body><div id='lobby'></div><div id='pv'></div><div id='ov'><h1></h1></div><div id='ced'></div><div id='fire'></div><div id='bzSquadOrders'></div></body></html>", encoding="utf-8")
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    first = html.read_text(encoding="utf-8")
    css = html.parent / "css/v6-screen-lifecycle.css"
    js = html.parent / "js/v6-screen-lifecycle.js"
    assert css.is_file() and js.is_file()
    subprocess.run([sys.executable, str(patcher), str(root)], check=True)
    assert first == html.read_text(encoding="utf-8"), "patcher must be idempotent"
    css_text = css.read_text(encoding="utf-8")
    js_text = js.read_text(encoding="utf-8")
    for token in ('data-bz-screen="gameplay"', 'data-bz-screen="results"', '#fire', '#bzSquadOrders', 'safe-area-inset-top', '#pvb', '#lb-l'):
        assert token in css_text, f"missing CSS lifecycle rule: {token}"
    for token in ("MutationObserver", "controls-edit", "classList.contains('on')", "ELIMINATED|WINNER", "bz:screen-change"):
        assert token in js_text, f"missing runtime lifecycle behaviour: {token}"
    assert "BATTLEZONE_V6_SCREEN_LIFECYCLE_REPAIR_V1" in first
    bad = root / "bad"
    (bad / "app/src/main/assets/www").mkdir(parents=True)
    (bad / "app/src/main/assets/www/index.html").write_text("<html></html>", encoding="utf-8")
    failed = subprocess.run([sys.executable, str(patcher), str(bad)], capture_output=True, text=True)
    assert failed.returncode != 0, "patcher must fail closed on unknown source"
print("SCREEN_LIFECYCLE_REPAIR_TESTS_OK idempotent=true screen_gating=true safe_areas=true fail_closed=true")
