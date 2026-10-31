"""Carga de animales (carpetas de frames PNG), composición y exportación a GIF."""
import colorsys
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

STAGES = ["baby", "young", "adult"]
ANIMATIONS = ["idle", "active", "eat", "sleep"]
DEFAULTS = {"fps": 6, "scale": 2, "recolor": []}


def load_config(animal_dir: Path) -> dict:
    path = animal_dir / "animal.json"
    return DEFAULTS | (json.loads(path.read_text()) if path.exists() else {})


def fps_for(config: dict, animation: str) -> float:
    """`fps` puede ser un número o un dict por animación: {"idle": 1.5, "active": 4}."""
    fps = config["fps"]
    return fps.get(animation, DEFAULTS["fps"]) if isinstance(fps, dict) else fps


def _natural_key(path: Path):
    # "2.png" antes que "10.png"
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.stem)]


def _load(path: Path) -> Image.Image:
    with Image.open(path) as img:
        return img.convert("RGBA")


def find_frames(animal_dir: Path, stage: str, animation: str) -> tuple[Path, list[Image.Image]]:
    """Frames de stage/animation. Si faltan: misma etapa con idle, luego la etapa más
    cercana (la menor si empatan). Devuelve también la carpeta usada."""
    i = STAGES.index(stage)
    stages = sorted(STAGES, key=lambda s: (abs(STAGES.index(s) - i), STAGES.index(s) > i))
    for s in stages:
        for a in dict.fromkeys([animation, "idle"]):
            folder = animal_dir / s / a
            files = sorted(folder.glob("*.png"), key=_natural_key)
            if files:
                return folder, [_load(f) for f in files]
    raise FileNotFoundError(f"{animal_dir}: no frames found; at least adult/idle/01.png is required")


def canvas_size(animal_dir: Path) -> tuple[int, int]:
    """Lienzo común a todo el animal, para que el GIF no cambie de tamaño entre días."""
    sizes = []
    for f in animal_dir.glob("*/*/*.png"):
        with Image.open(f) as img:
            sizes.append(img.size)
    return max(w for w, _ in sizes), max(h for _, h in sizes)


def palette(animal_dir: Path) -> Counter:
    """Colores opacos de todos los frames del animal ("#rrggbb" -> píxeles), para elegir `recolor`."""
    counts = Counter()
    for f in animal_dir.glob("*/*/*.png"):
        counts.update("#%02x%02x%02x" % p[:3] for p in _load(f).get_flattened_data() if p[3])
    return counts


def compose(frames: list[Image.Image], canvas: tuple[int, int], scale: int) -> list[Image.Image]:
    """Centra cada frame apoyado en el suelo (borde inferior) y escala sin suavizar."""
    w, h = canvas
    out = []
    for frame in frames:
        c = Image.new("RGBA", canvas)
        c.alpha_composite(frame, ((w - frame.width) // 2, h - frame.height))
        out.append(c.resize((w * scale, h * scale), Image.NEAREST))
    return out


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def recolor(frames: list[Image.Image], groups: list[list[str]], colors: list[str]) -> list[Image.Image]:
    """El grupo i de colores del sprite toma el tono y la saturación del color i
    (lenguaje i), conservando el brillo de cada píxel para no perder el sombreado."""
    mapping = {}
    for group, color in zip(groups, colors):
        hue, sat, _ = colorsys.rgb_to_hsv(*(c / 255 for c in _rgb(color)))
        for source in group:
            rgb = _rgb(source)
            value = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))[2]
            mapping[rgb] = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, value))
    out = []
    for frame in frames:
        frame = frame.copy()
        frame.putdata([(*mapping.get(p[:3], p[:3]), p[3]) for p in frame.get_flattened_data()])
        out.append(frame)
    return out


def save_gif(frames: list[Image.Image], path: Path, fps: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=round(1000 / fps), loop=0, disposal=2)


def remove_background(img: Image.Image, tolerance: int = 48) -> Image.Image:
    """Hace transparente el fondo liso que toca las esquinas (relleno por inundación,
    así no se borran zonas interiores del mismo color rodeadas por el contorno)."""
    img = img.convert("RGBA")
    for xy in [(0, 0), (img.width - 1, 0), (0, img.height - 1), (img.width - 1, img.height - 1)]:
        if img.getpixel(xy)[3]:
            ImageDraw.floodfill(img, xy, (0, 0, 0, 0), thresh=tolerance)
    return img


def pixelize_set(images: list[Image.Image], size: int, colors: int = 16) -> list[Image.Image]:
    """Reduce varias imágenes con la misma escala (el lado mayor de la más grande pasa a
    `size` px) y una paleta común, para que los frames no cambien de tamaño ni de color."""
    factor = size / max(max(img.size) for img in images)
    small = [img.resize((max(1, round(img.width * factor)), max(1, round(img.height * factor))),
                        Image.LANCZOS) for img in images]
    opaque = [p[:3] for img in small for p in img.get_flattened_data() if p[3] >= 128]
    strip = Image.new("RGB", (max(1, len(opaque)), 1))
    strip.putdata(opaque)
    palette = strip.quantize(colors)
    out = []
    for img in small:
        alpha = img.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
        frame = img.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
        frame.putalpha(alpha)
        out.append(frame.crop(alpha.getbbox()) if alpha.getbbox() else frame)
    return out


def breathe(frame: Image.Image, cut: float = 0.6) -> Image.Image:
    """Baja 1 px todo lo que está por encima de `cut` (fracción de la altura) y deja las
    patas quietas: respiración sutil de pixel art."""
    y = round(frame.height * cut)
    out = Image.new("RGBA", frame.size)
    out.alpha_composite(frame.crop((0, y, frame.width, frame.height)), (0, y))
    out.alpha_composite(frame.crop((0, 0, frame.width, y)), (0, 1))
    return out


def make_animal(src: Path, animal_dir: Path, sizes=(16, 24, 32), colors: int = 16) -> None:
    """Crea una carpeta de animal desde una imagen: una resolución por etapa y un
    idle genérico de dos frames (bote de 1 px). El resto de animaciones caen a idle.
    Si la imagen no tiene transparencia, se quita el fondo liso de las esquinas."""
    # ponytail: solo animación genérica de bote; añadir sleep/eat genéricos cuando se vea el resultado
    img = _load(src)
    if img.getextrema()[3][0] == 255:
        img = remove_background(img)
    for stage, size in zip(STAGES, sizes):
        base = pixelize_set([img], size, colors)[0]
        folder = animal_dir / stage / "idle"
        folder.mkdir(parents=True, exist_ok=True)
        for n, dy in enumerate([1, 0], start=1):
            frame = Image.new("RGBA", (base.width, base.height + 1))
            frame.alpha_composite(base, (0, dy))
            frame.save(folder / f"{n:02}.png")
