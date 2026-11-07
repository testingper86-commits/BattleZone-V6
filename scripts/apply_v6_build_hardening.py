#!/usr/bin/env python3
"""Harden build inputs, URI validation, asset packaging and Android unit-test coverage."""
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
marker = "BATTLEZONE_V6_BUILD_HARDENING_V1"

def one(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)

gradle_path = root / "app/build.gradle.kts"
models_path = root / "app/src/main/assets/www/js/models.js"
activity_path = root / "app/src/main/java/com/example/battlezone/MainActivity.kt"
if not all(p.is_file() for p in (gradle_path, models_path, activity_path)):
    raise SystemExit("Android Gradle, model loader, or MainActivity source is missing")

gradle = gradle_path.read_text(encoding="utf-8")
models = models_path.read_text(encoding="utf-8")
activity = activity_path.read_text(encoding="utf-8")
validator_path = root / "validate_project.py"
if validator_path.is_file():
    validator = validator_path.read_text(encoding="utf-8")
    if "downloadOptionalLibs" in validator:
        validator = validator.replace("downloadOptionalLibs", "downloadCharacterRuntimeLibraries")
        validator_path.write_text(validator, encoding="utf-8")

if marker not in gradle:
    gradle = one(gradle, "import java.net.URL\nimport java.util.zip.ZipInputStream\n", "import java.net.URL\nimport java.nio.file.Files\nimport java.nio.file.StandardCopyOption\nimport java.security.MessageDigest\n", "build-hardening imports")
    gradle = one(gradle, '        versionCode = 1\n        versionName = "1.0"', '        versionCode = 2\n        versionName = "1.1.0"', "Android version increment")
    gradle = one(gradle, '    implementation("androidx.core:core-ktx:1.15.0")\n', '    implementation("androidx.core:core-ktx:1.15.0")\n    testImplementation("junit:junit:4.13.2")\n', "JUnit dependency")
    gradle = one(gradle, '//   * GLTFLoader + SkeletonUtils r128 and soldier.glb - OPTIONAL (rigged remote-player model);\n//     if they cannot be fetched the game keeps its built-in procedural characters.\n', '//   * GLTFLoader, FBXLoader, SkeletonUtils and fflate r128 - REQUIRED for bundled rigged models.\n', "runtime library documentation")
    old_download = '''fun download(urls: List<String>, target: File, minSize: Long, mustContain: String?, errors: MutableList<String>): Boolean {
    target.parentFile.mkdirs()
    for (src in urls) {
        try {
            val c = URL(src).openConnection() as HttpURLConnection
            c.connectTimeout = 15_000; c.readTimeout = 90_000
            c.setRequestProperty("User-Agent", "BattleZone-Gradle"); c.instanceFollowRedirects = true
            if (c.responseCode != 200) { errors += "$src -> HTTP ${c.responseCode}"; continue }
            val tmp = File(target.parentFile, target.name + ".download")
            c.inputStream.use { i -> tmp.outputStream().use { o -> i.copyTo(o) } }
            val ok = tmp.length() >= minSize && (mustContain == null || tmp.readText(Charsets.ISO_8859_1).contains(mustContain))
            if (!ok) { tmp.delete(); errors += "$src -> unexpected content"; continue }
            if (target.exists()) target.renameTo(File(target.parentFile, target.name + ".replaced-backup"))
            tmp.renameTo(target)
            logger.lifecycle("Downloaded ${target.name} (${target.length() / 1024} KB) from $src")
            return true
        } catch (e: Exception) { errors += "$src -> ${e.javaClass.simpleName}: ${e.message}" }
    }
    return false
}'''
    new_download = '''fun sha256(file: File): String = MessageDigest.getInstance("SHA-256")
    .digest(file.readBytes()).joinToString("") { "%02x".format(it.toInt() and 0xff) }

fun download(
    urls: List<String>, target: File, minSize: Long, mustContain: String?,
    errors: MutableList<String>, expectedSha256: String
): Boolean {
    target.parentFile.mkdirs()
    for (src in urls) {
        val tmp = File(target.parentFile, target.name + ".download")
        var connection: HttpURLConnection? = null
        try {
            connection = URL(src).openConnection() as HttpURLConnection
            connection.connectTimeout = 15_000
            connection.readTimeout = 90_000
            connection.setRequestProperty("User-Agent", "BattleZone-Gradle")
            connection.instanceFollowRedirects = true
            if (connection.responseCode != 200) {
                errors += "$src -> HTTP ${connection.responseCode}"
                continue
            }
            connection.inputStream.use { input -> tmp.outputStream().buffered().use { output -> input.copyTo(output) } }
            val contentValid = tmp.length() >= minSize &&
                (mustContain == null || tmp.readText(Charsets.ISO_8859_1).contains(mustContain))
            val hashValid = sha256(tmp).equals(expectedSha256, ignoreCase = true)
            if (!contentValid || !hashValid) {
                tmp.delete()
                errors += "$src -> content validation or SHA-256 verification failed"
                continue
            }
            Files.move(tmp.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING)
            logger.lifecycle("Verified and installed ${target.name} (${target.length() / 1024} KB) from $src")
            return true
        } catch (e: Exception) {
            tmp.delete()
            errors += "$src -> ${e.javaClass.simpleName}: ${e.message}"
        } finally {
            connection?.disconnect()
        }
    }
    return false
}'''
    gradle = one(gradle, old_download, new_download, "verified atomic dependency downloader")
    old_three = '''val threeTarget = File(wwwDir, "libs/three.min.js")
fun looksLikeThree(f: File): Boolean =
    f.isFile && f.length() > 300_000 && f.readText(Charsets.ISO_8859_1).contains("REVISION")
// Exact version when the build states it ("REVISION=\\"128\\""), loose literal match otherwise.
fun isThreeR128(f: File): Boolean {
    if (!looksLikeThree(f)) return false
    val text = f.readText(Charsets.ISO_8859_1)
    val m = Regex("REVISION\\\\s*=\\\\s*[\\\"'](\\\\d+)[\\\"']").find(text)
    return if (m != null) m.groupValues[1] == "128" else Regex("[\\\"']128[\\\"']").containsMatchIn(text)
}'''
    new_three = '''val threeTarget = File(wwwDir, "libs/three.min.js")
val THREE_R128_SHA256 = "9274bbcec8d96168626c732b5d31c775aa8cfb7eaa0599bec0c175908a2c1ce2"
fun looksLikeThree(f: File): Boolean =
    f.isFile && f.length() > 300_000 && f.readText(Charsets.ISO_8859_1).contains("REVISION")
fun isThreeR128(f: File): Boolean = looksLikeThree(f) && sha256(f).equals(THREE_R128_SHA256, ignoreCase = true)'''
    gradle = one(gradle, old_three, new_three, "Three.js checksum pin")
    gradle = one(gradle, '            "https://unpkg.com/three@0.128.0/build/three.min.js"), threeTarget, 300_000, "REVISION", errors)', '            "https://unpkg.com/three@0.128.0/build/three.min.js"), threeTarget, 300_000, "REVISION", errors, THREE_R128_SHA256)', "Three.js verified download")
    warning_anchor = '            if (looksLikeThree(threeTarget)) logger.warn('
    warning_start = gradle.find(warning_anchor)
    if warning_start < 0:
        raise SystemExit("unverified Three.js fallback warning anchor not found")
    first_line_end = gradle.find("\n", warning_start)
    second_line_end = gradle.find("\n", first_line_end + 1)
    if first_line_end < 0 or second_line_end < 0 or "else throw GradleException(msg)" not in gradle[first_line_end:second_line_end]:
        raise SystemExit("unverified Three.js fallback branch changed unexpectedly")
    gradle = gradle[:warning_start] + "            throw GradleException(msg)" + gradle[second_line_end:]
    start = gradle.index("// ---- Optional loaders (r128 classic builds from the three.js examples folder) ----")
    end = gradle.index("tasks.matching { it.name == \"preBuild\" }", start)
    new_section = '''// ---- Required, version-pinned runtime loaders (Three.js r128 classic builds) ----
val downloadCharacterRuntimeLibraries = tasks.register("downloadCharacterRuntimeLibraries") {
    group = "battlezone"
    description = "Installs checksum-pinned Three.js r128 character loaders required by the bundled rigs."
    doLast {
        val required = listOf(
            Triple("loaders/GLTFLoader.js", "GLTFLoader.js", "5c15967ba830918a9caea6338712c994c354bccd4edc4569bde411c3ec06a3e6"),
            Triple("loaders/FBXLoader.js", "FBXLoader.js", "a5732b0dcdf530ecfd5ff21eb96e9343fc8e40dd75e548730352e6cfb79342b1"),
            Triple("utils/SkeletonUtils.js", "SkeletonUtils.js", "cc2e2e1a3183ab55169d185565f86f43f80c6dfafe73610d991e741ea990ac1a"),
            Triple("libs/fflate.min.js", "fflate.min.js", "798b397d482f2ff743452362e880f1be4b683c43d7b2db3e8751f7412e7d5f4b")
        )
        required.forEach { (path, name, expectedHash) ->
            val target = File(wwwDir, "libs/$name")
            if (target.isFile && sha256(target).equals(expectedHash, ignoreCase = true)) return@forEach
            val errors = mutableListOf<String>()
            val ok = download(
                listOf(
                    "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/$path",
                    "https://unpkg.com/three@0.128.0/examples/js/$path"
                ), target, 5_000, null, errors, expectedHash
            )
            if (!ok) throw GradleException("Could not obtain verified $name.\\n  " + errors.joinToString("\\n  "))
        }
    }
}

'''
    gradle = gradle[:start] + new_section + gradle[end:]
    gradle = one(gradle, 'dependsOn(downloadThreeJs, downloadOptionalLibs)   // downloadSoldierModels is manual/optional (Kenney is bundled)', 'dependsOn(downloadThreeJs, downloadCharacterRuntimeLibraries) // all runtime libraries are checksum-pinned', "required runtime dependency tasks")
    gradle = gradle.replace("// BATTLEZONE_V6_BUILD_HARDENING_V1", "", 1) if marker in gradle else gradle
    gradle += "\n// " + marker + "\n"

# Remove the absent, never-built soldier fallback. Kenney remains primary; KayKit is the bundled fallback.
soldier_entry = " {format:'glb',model:'./models/characters/soldier.glb',height:1.8,yawOffset:0}"
if soldier_entry in models:
    models = one(models, soldier_entry, "", "obsolete absent soldier fallback")
models = models.replace("else soldier.glb.", "else the bundled KayKit GLB.")

# Route all origin checks through a pure Kotlin policy that can be covered by real JVM unit tests.
old_helper = '''    private fun isTrustedAssetUri(uri: Uri): Boolean {
        return uri.scheme == "https" &&
            uri.host == "appassets.androidplatform.net" &&
            (uri.port == -1 || uri.port == 443) &&
            uri.userInfo == null &&
            (uri.path?.let { path ->
                path.startsWith("/assets/") && path.split('/').none { it == "." || it == ".." }
            } == true)
    }'''
new_helper = '''    private fun isTrustedAssetUri(uri: Uri): Boolean = OfflineAssetPolicy.isTrustedAssetUri(
        uri.scheme, uri.host, uri.port, uri.userInfo, uri.path
    )'''
if "OfflineAssetPolicy.isTrustedAssetUri" not in activity:
    activity = one(activity, old_helper, new_helper, "centralized offline asset URI policy")

policy_path = root / "app/src/main/java/com/example/battlezone/OfflineAssetPolicy.kt"
policy_path.parent.mkdir(parents=True, exist_ok=True)
policy_path.write_text('''package com.example.battlezone

import java.net.URLDecoder

/** Pure URI policy shared by the WebView host and JVM regression tests. */
internal object OfflineAssetPolicy {
    fun isTrustedAssetUri(
        scheme: String?,
        host: String?,
        port: Int,
        userInfo: String?,
        path: String?
    ): Boolean {
        if (!scheme.equals("https", ignoreCase = true)) return false
        if (!host.equals("appassets.androidplatform.net", ignoreCase = true)) return false
        if (port != -1 && port != 443) return false
        if (userInfo != null || path == null) return false

        val decoded = decodePath(path) ?: return false
        if (!decoded.startsWith("/assets/") || '\\\\' in decoded) return false
        return decoded.split('/').none { it == "." || it == ".." }
    }

    private fun decodePath(path: String): String? {
        var current = path
        repeat(4) {
            val decoded = try {
                URLDecoder.decode(current.replace("+", "%2B"), "UTF-8")
            } catch (_: IllegalArgumentException) {
                return null
            }
            if (decoded == current) return current
            current = decoded
        }
        // Refuse deeply nested encodings instead of allowing a later URL layer to reinterpret them.
        if (Regex("(?i)%2e|%2f|%5c").containsMatchIn(current)) return null
        return current
    }
}
''', encoding="utf-8")

unit_test_path = root / "app/src/test/java/com/example/battlezone/OfflineAssetPolicyTest.kt"
unit_test_path.parent.mkdir(parents=True, exist_ok=True)
unit_test_path.write_text('''package com.example.battlezone

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class OfflineAssetPolicyTest {
    private fun allowed(path: String?, scheme: String = "https", host: String = "appassets.androidplatform.net", port: Int = -1, userInfo: String? = null) =
        OfflineAssetPolicy.isTrustedAssetUri(scheme, host, port, userInfo, path)

    @Test fun acceptsOnlyTheLocalHttpsAssetOrigin() {
        assertTrue(allowed("/assets/www/index.html"))
        assertTrue(allowed("/assets/www/index.html", port = 443))
        assertFalse(allowed("/assets/www/index.html", scheme = "http"))
        assertFalse(allowed("/assets/www/index.html", host = "example.com"))
        assertFalse(allowed("/assets/www/index.html", port = 444))
        assertFalse(allowed("/assets/www/index.html", userInfo = "attacker"))
    }

    @Test fun rejectsPathsOutsideTheAssetRoot() {
        assertFalse(allowed(null))
        assertFalse(allowed("/assets"))
        assertFalse(allowed("/private/index.html"))
        assertFalse(allowed("/assets2/index.html"))
    }

    @Test fun rejectsLiteralAndEncodedTraversal() {
        assertFalse(allowed("/assets/../private/file"))
        assertFalse(allowed("/assets/%2e%2e/private/file"))
        assertFalse(allowed("/assets/%252e%252e/private/file"))
        assertFalse(allowed("/assets/sub%2f..%2fprivate/file"))
        assertFalse(allowed("/assets/..\\\\private/file"))
    }

    @Test fun rejectsMalformedOrExcessivelyNestedEncoding() {
        assertFalse(allowed("/assets/%ZZ/file"))
        assertFalse(allowed("/assets/%25252e%25252e/private/file"))
    }
}
''', encoding="utf-8")

# Prune every KayKit item not referenced by the active loader; retain only its rigged GLB and CC0 license.
kaykit = root / "app/src/main/assets/www/models/characters/kaykit_v1_2"
if kaykit.is_dir():
    keep = {
        Path("License.txt"),
        Path("Animations/gltf/KayKit_AnimatedCharacter_v1.2.glb"),
    }
    for item in sorted(kaykit.rglob("*"), reverse=True):
        if item.is_file() and item.relative_to(kaykit) not in keep:
            item.unlink()
        elif item.is_dir() and not any(item.iterdir()):
            item.rmdir()
    required = [kaykit / relative for relative in keep]
    if not all(item.is_file() for item in required):
        raise SystemExit("KayKit fallback GLB or its CC0 license is missing")

# The active renderer uses the root PBR texture set; this duplicated starter environment pack is unused.
shutil.rmtree(root / "app/src/main/assets/www/assets/environment", ignore_errors=True)

gradle_path.write_text(gradle, encoding="utf-8")
models_path.write_text(models, encoding="utf-8")
activity_path.write_text(activity, encoding="utf-8")
print(marker, "version=1.1.0", "junit=4", "pinned-libraries=5", "kaykit-assets=GLB+license", "unused-environment-pack=removed")
