#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import tempfile
import zipfile

SCRIPT = Path(__file__).with_name("verify_offline_integrity.py")
spec = importlib.util.spec_from_file_location("verify_offline_integrity", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(root: Path) -> None:
    (root / "app/src/main/java/com/example/battlezone").mkdir(parents=True)
    (root / "app/src/main/assets/www/js").mkdir(parents=True)
    (root / "app/src/main/assets/www/css").mkdir(parents=True)
    (root / "app/src/main/AndroidManifest.xml").write_text("<manifest package='test' />", encoding="utf-8")
    (root / "app/src/main/java/com/example/battlezone/MainActivity.kt").write_text(
        "class MainActivity { val offline = true; settings.blockNetworkLoads = true }", encoding="utf-8"
    )
    html = """<meta http-equiv="Content-Security-Policy" content="default-src 'self'; connect-src 'self'"><script src="./js/game.js"></script>"""
    (root / "app/src/main/assets/www/index.html").write_text(html, encoding="utf-8")
    (root / "app/src/main/assets/www/js/models.js").write_text("const localModels = true;", encoding="utf-8")
    (root / "app/src/main/assets/www/css/game.css").write_text("body { background: #000; }", encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    fixture(root)
    assert module.verify_source(root) == [], module.verify_source(root)

    manifest = root / "app/src/main/AndroidManifest.xml"
    manifest.write_text("<uses-permission android:name='android.permission.INTERNET'/>", encoding="utf-8")
    assert any("network permission" in item for item in module.verify_source(root))
    manifest.write_text("<manifest/>", encoding="utf-8")

    activity = root / "app/src/main/java/com/example/battlezone/MainActivity.kt"
    activity.write_text("WifiManager", encoding="utf-8")
    assert any("WifiManager" in item for item in module.verify_source(root))
    activity.write_text("offline", encoding="utf-8")

    (root / "app/src/main/assets/www/js/netplay.js").write_text("legacy", encoding="utf-8")
    assert any("netplay.js" in item for item in module.verify_source(root))
    (root / "app/src/main/assets/www/js/netplay.js").unlink()

    css = root / "app/src/main/assets/www/css/game.css"
    css.write_text('@import url("https://cdn.example.com/game.css");', encoding="utf-8")
    assert any("external runtime resource" in item for item in module.verify_source(root))
    css.write_text("body { background: #000; }", encoding="utf-8")

    js = root / "app/src/main/assets/www/js/game.js"
    js.write_text('fetch("https://api.example.com/match");', encoding="utf-8")
    assert any("external runtime resource" in item for item in module.verify_source(root))
    js.write_text('fetch("./local-data.json");', encoding="utf-8")

    html = root / "app/src/main/assets/www/index.html"
    html.write_text('<script src="https://cdn.example.com/game.js"></script>', encoding="utf-8")
    assert any("remote script source" in item or "external runtime resource" in item for item in module.verify_source(root))
    fixture(root)

    apk = root / "fixture.apk"
    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr("AndroidManifest.xml", b"<manifest android.permission.INTERNET/>")
        archive.writestr("assets/www/index.html", b"<html/>")
    assert any("network permission" in item for item in module.verify_apk(apk))

    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr("AndroidManifest.xml", b"<manifest/>")
        archive.writestr("classes.dex", b"GameNetworkBridge")
    assert any("GameNetworkBridge" in item for item in module.verify_apk(apk))

    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr("AndroidManifest.xml", b"<manifest/>")
        archive.writestr("assets/www/css/game.css", b'@import url("https://cdn.example.com/game.css");')
    assert any("external runtime resource" in item for item in module.verify_apk(apk))

print("OFFLINE_INTEGRITY_FIXTURE_TESTS_OK")
