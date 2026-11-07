#!/usr/bin/env python3
from pathlib import Path
import importlib.util, tempfile, zipfile
SCRIPT = Path(__file__).with_name("verify_offline_integrity.py")
spec = importlib.util.spec_from_file_location("verify_offline_integrity", SCRIPT)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def fixture(root: Path):
    (root / "app/src/main/java/com/example/battlezone").mkdir(parents=True)
    (root / "app/src/main/assets/www/js").mkdir(parents=True)
    (root / "app/src/main/AndroidManifest.xml").write_text("<manifest package='test' />", encoding="utf-8")
    (root / "app/src/main/java/com/example/battlezone/MainActivity.kt").write_text("class MainActivity { val offline = true; settings.blockNetworkLoads = true }", encoding="utf-8")
    html = """<meta http-equiv="Content-Security-Policy" content="default-src 'self'; connect-src 'self'"><script src="./js/game.js"></script>"""
    (root / "app/src/main/assets/www/index.html").write_text(html, encoding="utf-8")
    (root / "app/src/main/assets/www/js/models.js").write_text("const localModels = true;", encoding="utf-8")
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp); fixture(root)
    assert module.verify_source(root) == [], module.verify_source(root)
    manifest=root/"app/src/main/AndroidManifest.xml"
    manifest.write_text("<uses-permission android:name='android.permission.INTERNET'/>", encoding="utf-8")
    assert any("network permission" in item for item in module.verify_source(root))
    manifest.write_text("<manifest/>", encoding="utf-8")
    (root/"app/src/main/java/com/example/battlezone/MainActivity.kt").write_text("WifiManager", encoding="utf-8")
    assert any("WifiManager" in item for item in module.verify_source(root))
    (root/"app/src/main/java/com/example/battlezone/MainActivity.kt").write_text("offline", encoding="utf-8")
    (root/"app/src/main/assets/www/js/netplay.js").write_text("legacy", encoding="utf-8")
    assert any("netplay.js" in item for item in module.verify_source(root))
    apk=root/"fixture.apk"
    with zipfile.ZipFile(apk,"w") as z:
        z.writestr("AndroidManifest.xml",b"<manifest android.permission.INTERNET/>")
        z.writestr("assets/www/index.html",b"<html/>")
    assert any("network permission" in item for item in module.verify_apk(apk))
    with zipfile.ZipFile(apk,"w") as z:
        z.writestr("AndroidManifest.xml",b"<manifest/>")
        z.writestr("classes.dex",b"GameNetworkBridge")
    assert any("GameNetworkBridge" in item for item in module.verify_apk(apk))
print("OFFLINE_INTEGRITY_FIXTURE_TESTS_OK")
