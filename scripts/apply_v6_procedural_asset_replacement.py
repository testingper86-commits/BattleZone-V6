#!/usr/bin/env python3
"""Replace unproven image assets with deterministic original procedural artwork.

The original archive remains untouched. This transformation runs only against the
CI-extracted distributable source tree and records exact generated-file hashes.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

GENERATOR = "BattleZone-V6-Procedural-Assets"
GENERATOR_VERSION = "1.0.0"
SIZE = 512
MATERIALS = {
    "asphalt": ((43, 47, 49), (74, 78, 78)),
    "bark": ((53, 35, 25), (126, 83, 51)),
    "concrete": ((83, 87, 87), (151, 151, 142)),
    "dry_dirt": ((83, 51, 30), (157, 111, 67)),
    "forest_floor": ((35, 49, 29), (110, 91, 51)),
    "grass": ((28, 59, 24), (104, 133, 51)),
    "military_metal": ((42, 49, 39), (111, 119, 94)),
    "sand": ((129, 102, 64), (211, 183, 132)),
    "weathered_rock": ((57, 57, 53), (142, 133, 113)),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clamp(v: float) -> int:
    return max(0, min(255, int(v)))


def periodic_field(x: int, y: int, seed: int) -> float:
    # Integer spatial frequencies make the broad procedural field tileable.
    return (
        0.34 * math.sin((x * 2 * math.pi / SIZE) * (3 + seed % 3) + seed)
        + 0.25 * math.cos((y * 2 * math.pi / SIZE) * (4 + seed % 4) + seed * 0.7)
        + 0.19 * math.sin((x + y) * 2 * math.pi / SIZE * 5 + seed * 1.3)
        + 0.12 * math.cos((2 * x - y) * 2 * math.pi / SIZE * 7 + seed * 0.3)
    )


def make_material(path: Path, material: str, channel: str) -> None:
    seed = int(hashlib.sha256(f"{material}:{channel}:v1".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    low, high = MATERIALS[material]
    pixels = []
    for y in range(SIZE):
        for x in range(SIZE):
            field = periodic_field(x, y, seed % 997)
            grain = rng.uniform(-0.11, 0.11)
            if material == "bark":
                grain += 0.22 * math.sin(x * 2 * math.pi / 38 + 2.0 * math.sin(y / 29))
            elif material == "military_metal":
                grain += 0.12 * math.sin((x + y * 0.12) * 2 * math.pi / 71)
            elif material == "grass":
                grain += 0.12 * math.sin((x * 0.7 + y * 1.1) * 2 * math.pi / 23)
            if channel == "height":
                v = clamp(128 + field * 76 + grain * 110)
                pixels.append((v, v, v))
            elif channel == "roughness":
                base = 202 if material in {"asphalt", "concrete", "military_metal"} else 226
                v = clamp(base + field * 20 + grain * 70)
                pixels.append((v, v, v))
            else:
                t = max(0.0, min(1.0, 0.5 + field * 0.34 + grain))
                pixels.append(tuple(clamp(a + (b - a) * t) for a, b in zip(low, high)))
    image = Image.new("RGB", (SIZE, SIZE))
    image.putdata(pixels)
    # A subtle tile-preserving sharpen restores surface detail after filtering.
    image.save(path, format="PNG", optimize=True)


def make_sprite(path: Path, kind: str) -> None:
    size = 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = image.load()
    rng = random.Random(int(hashlib.sha256((kind + ":sprite:v1").encode()).hexdigest()[:8], 16))
    for y in range(size):
        for x in range(size):
            nx, ny = (x - 127.5) / 127.5, (y - 127.5) / 127.5
            r = math.sqrt(nx * nx + ny * ny)
            angle = math.atan2(ny, nx)
            if kind == "vegetation_blades":
                blade = max(0.0, math.sin(angle * 11 + 0.8 * math.sin(r * 12)))
                alpha = int(230 * blade * max(0.0, 1 - r) ** 1.7) if r < 1 else 0
                color = (79 + int(45 * blade), 105 + int(65 * blade), 35, alpha)
            elif kind == "impact_spark":
                rays = abs(math.sin(angle * 9))
                alpha = int(255 * max(0.0, 1 - r) ** 2 * (0.22 + 0.78 * rays)) if r < 1 else 0
                color = (255, 218 + int(30 * (1-r)), 126, alpha)
            elif kind == "muzzle_flash":
                shape = max(0.0, math.cos(angle * 4)) ** 3
                alpha = int(255 * max(0.0, 1-r) ** 1.8 * shape) if r < 1 else 0
                color = (255, 205 + int(40 * (1-r)), 111, alpha)
            elif kind == "smoke_puff":
                cloud = max(0.0, 1 - r + 0.12 * math.sin(angle * 5 + r * 8))
                alpha = int(170 * cloud ** 2) if r < 1.08 else 0
                shade = 105 + int(75 * cloud)
                color = (shade, shade + 5, shade + 9, alpha)
            else:  # dust_puff
                cloud = max(0.0, 1 - r + 0.09 * math.sin(angle * 7 + r * 11))
                alpha = int(190 * cloud ** 2) if r < 1.05 else 0
                color = (171, 139, 92, alpha)
            px[x, y] = color
    image = image.filter(ImageFilter.GaussianBlur(1.2))
    image.save(path, format="PNG", optimize=True)


def make_loading(path: Path, index: int) -> None:
    w, h = 1280, 720
    image = Image.new("RGB", (w, h))
    px = image.load()
    top = (18 + index * 3, 28 + index * 2, 30 + index * 2)
    bottom = (65 + index * 4, 76 + index * 3, 62 + index * 2)
    for y in range(h):
        t = y / (h - 1)
        band = 5 * math.sin(t * math.pi * 3 + index)
        color = tuple(clamp(a + (b-a)*t + band) for a,b in zip(top,bottom))
        for x in range(w):
            noise = ((x * 17 + y * 31 + index * 101) % 19) - 9
            px[x,y] = tuple(clamp(c + noise) for c in color)
    draw = ImageDraw.Draw(image, "RGBA")
    # Original layered ridgelines and a sparse tactical grid, no copied imagery.
    for layer, base in enumerate((500, 555, 620)):
        points = [(0, h)]
        for x in range(0, w + 41, 40):
            yy = base + 34 * math.sin(x / (115 + layer * 17) + index * 0.8 + layer) + 17 * math.sin(x / 53 + layer)
            points.append((x, int(yy)))
        points.append((w, h))
        draw.polygon(points, fill=((26+layer*7, 39+layer*5, 31+layer*3, 220)))
    for x in range(0,w,80): draw.line((x,0,x,h), fill=(178,190,157,13), width=1)
    for y in range(0,h,80): draw.line((0,y,w,y), fill=(178,190,157,13), width=1)
    draw.ellipse((820,90,1110,380), outline=(194,174,117,50), width=2)
    draw.ellipse((870,140,1060,330), outline=(194,174,117,35), width=2)
    image.save(path, format="JPEG", quality=88, optimize=True, progressive=False)


def make_logo(path: Path) -> None:
    w, h = 1024, 512
    image = Image.new("RGB", (w,h), (18,25,23))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(h):
        c = int(18 + 22*y/h)
        draw.line((0,y,w,y), fill=(c,c+7,c+3,255))
    draw.polygon([(115,256),(230,100),(345,256),(230,412)], fill=(135,157,105,255), outline=(210,219,180,255))
    draw.polygon([(230,155),(285,256),(230,357),(175,256)], fill=(23,34,29,255))
    draw.line((230,195,230,317), fill=(217,225,184,255), width=9)
    draw.line((169,256,291,256), fill=(217,225,184,255), width=9)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)
        sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 27)
    except OSError:
        font, sub = ImageFont.load_default(), ImageFont.load_default()
    draw.text((390,175), "BATTLE ZONE", font=font, fill=(235,239,217,255), stroke_width=1, stroke_fill=(10,14,12,255))
    draw.text((398,280), "V6  /  OFFLINE COMBAT", font=sub, fill=(166,185,143,255))
    draw.line((395,335,900,335), fill=(148,169,117,170), width=3)
    image.save(path, format="JPEG", quality=91, optimize=True, progressive=False)


def expected_paths() -> list[str]:
    paths = []
    for material in MATERIALS:
        for channel in ("basecolor", "height", "roughness"):
            paths.append(f"textures/{material}_{channel}.png")
    paths += [f"sprites/{name}.png" for name in ("dust_puff", "impact_spark", "muzzle_flash", "smoke_puff", "vegetation_blades")]
    paths += [f"loading/boot_scene_{i}.jpg" for i in (1,2,3)]
    paths += ["branding/battle_zone_logo.jpg"]
    return sorted(paths)


def apply(root: Path) -> dict:
    assets = root / "app/src/main/assets/www"
    if not assets.is_dir(): raise SystemExit(f"Missing runtime asset root: {assets}")
    generated = []
    for rel in expected_paths():
        path = assets / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith("textures/"):
            stem = path.stem
            material, channel = stem.rsplit("_",1)
            make_material(path, material, channel)
        elif rel.startswith("sprites/"):
            make_sprite(path, path.stem)
        elif rel.startswith("loading/"):
            make_loading(path, int(path.stem.rsplit("_",1)[1]))
        else:
            make_logo(path)
        generated.append({"path":rel,"sha256":sha256(path),"size_bytes":path.stat().st_size,"generator":GENERATOR,"generator_version":GENERATOR_VERSION,"license":"original_project_generated"})
    manifest = {"schema_version":1,"generator":GENERATOR,"generator_version":GENERATOR_VERSION,"license":"original_project_generated","license_basis":"Original procedural artwork generated by this project-specific deterministic generator; no third-party source images or textures are embedded.","assets":generated}
    (assets / "PROCEDURAL_ASSET_PROVENANCE.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    result = apply(root)
    print(f"PROCEDURAL_ASSET_REPLACEMENT_OK assets={len(result['assets'])} generator={GENERATOR}@{GENERATOR_VERSION}")
