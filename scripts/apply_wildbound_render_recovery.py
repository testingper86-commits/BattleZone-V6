#!/usr/bin/env python3
"""Validate canonical WebGL lifecycle recovery and install its offline UI styles."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def locate(relative):
    direct = root / relative
    if direct.is_file():
        return direct
    matches = list(root.rglob(relative))
    if len(matches) != 1:
        raise SystemExit(f"{relative}: expected exactly one file, found {len(matches)}")
    return matches[0]

runtime_path = locate("app/src/main/assets/www/js/wildbound/rendering/runtime.js")
css_path = locate("app/src/main/assets/www/css/wildbound.css")
runtime = runtime_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
marker = "WILDBOUND_RENDER_RECOVERY_V1"

old_binding = "T=()=>window.THREE"
if old_binding in runtime:
    if runtime.count(old_binding) != 1:
        raise SystemExit("Three.js accessor binding is duplicated; refusing unsafe normalization")
    runtime = runtime.replace(old_binding, "T=window.THREE", 1)
if runtime.count("T=window.THREE") != 1:
    raise SystemExit("Three.js namespace must be captured exactly once as an object")
if "let t=T();" in runtime:
    if runtime.count("let t=T();") != 1:
        raise SystemExit("Three.js scene initialization has multiple accessor calls")
    runtime = runtime.replace("let t=T();", "let t=T;", 1)
if "let t=T;" not in runtime:
    raise SystemExit("Three.js scene initialization must use the captured namespace object")

required = (
    "webglcontextlost", "webglcontextrestored", "event.preventDefault()",
    "isContextLost()", "WILDBOUND_RENDER_FRAME_ERROR", "WILDBOUND_LOBBY_RENDER_ERROR",
    "game.renderer.resetState()", "host.clientWidth", "host.clientHeight",
    "new ResizeObserver", "visualViewport", "getRenderDiagnostics", "canvasWidth",
    "WILDBOUND_RESUME_BLOCKED", "render-recovery", "WILDBOUND_CAMERA_RELATIVE_CONTROL_V1",
    "game.vfx.update(dt)", "W.world.update(game.environment,dt,game.elapsed)",
)
missing = [token for token in required if token not in runtime]
if missing:
    raise SystemExit("Canonical runtime is missing recovery features: " + ", ".join(missing))
if marker not in runtime:
    runtime = "/* " + marker + " */\n" + runtime

css_marker_count = css.count(marker)
if css_marker_count > 1:
    raise SystemExit("Render recovery CSS marker is duplicated")
if css_marker_count == 0:
    css += "\n/* " + marker + " */\n" + r"""
.render-recovery{display:none;position:fixed;z-index:1300;inset:0;box-sizing:border-box;align-items:center;justify-content:center;flex-direction:column;gap:12px;padding:calc(22px + env(safe-area-inset-top)) calc(20px + env(safe-area-inset-right)) calc(22px + env(safe-area-inset-bottom)) calc(20px + env(safe-area-inset-left));background:rgba(5,10,14,.96);color:#e7f0ed;text-align:center;overflow:auto}
.render-recovery.visible{display:flex}
.render-recovery-title{max-width:560px;color:#f1c58c;font-size:12px;font-weight:800;letter-spacing:.16em}
.render-recovery-copy{max-width:560px;margin:0;color:#c3d1cc;font-size:13px;line-height:1.55}
.render-recovery-detail{box-sizing:border-box;width:min(620px,100%);max-height:30vh;overflow:auto;margin:0;padding:12px;border:1px solid rgba(139,173,164,.25);background:rgba(20,31,35,.8);color:#a9bbb5;text-align:left;white-space:pre-wrap;overflow-wrap:anywhere;font:10px/1.45 ui-monospace,monospace}
.render-recovery-retry{width:min(420px,100%);min-height:46px}
"""
if css.count(marker) != 1 or ".render-recovery.visible" not in css:
    raise SystemExit("Render recovery UI styles failed their idempotency postcondition")

runtime_path.write_text(runtime, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print("WILDBOUND_RENDER_RECOVERY_CANONICAL_VALIDATED_AND_STYLED")
