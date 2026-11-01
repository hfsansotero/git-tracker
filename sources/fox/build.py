"""Construye animals/fox a partir de las imágenes generadas con Higgsfield.

  base.png   zorro de pie (seedream_v5_lite)
  poses.png  hoja 2x2 con base.png de referencia: carrera A | carrera B / dormido | comiendo

Ejecutar desde la raíz del repo: python sources/fox/build.py
"""
import colorsys
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from PIL import Image

from git_tracker.sprites import STAGES, breathe, pixelize_set, remove_background, split_zone

HERE = Path(__file__).parent
OUT = HERE.parents[1] / "animals" / "fox"
SIZES = (36, 50, 64)  # lado mayor del frame más grande en cada etapa
COLORS = 14
FPS = {"idle": 1.33, "active": 4, "sleep": 0.8, "eat": 2.67}
# The tail of each pose, measured in pixels on the adult frame (its size last), so it fits every stage.
# ponytail: hand-measured outlines; redo them if the poses are regenerated
TAILS = {
    "idle": ([(0, 14), (23, 13), (17, 28), (13, 37), (0, 37)], (62, 37)),
    "run_a": ([(0, 10), (23, 10), (19, 30), (0, 30)], (64, 35)),
    "run_b": ([(0, 10), (23, 10), (19, 30), (0, 30)], (64, 35)),
    "sleep": ([(0, 17), (20, 15), (28, 16), (31, 12), (41, 10), (41, 28), (0, 28)], (41, 28)),
    "eat": ([(0, 31), (0, 15), (17, 3), (21, 12), (14, 31)], (62, 31)),
}


def hsv(c):
    return colorsys.rgb_to_hsv(*(x / 255 for x in c))


def is_coat(c):
    hh, s, v = hsv(c)
    return hh < 0.12 and s > 0.45 and v > 0.35


def is_cream(c):
    hh, s, v = hsv(c)
    return s < 0.35 and v > 0.6


def zones(frame, pose):
    """Coat in the tail -> tail group; cream outside the tail (chest, cheeks) -> mane group.
    The cream tip of the tail keeps its color."""
    ORIGINAL.update(p[:3] for p in frame.get_flattened_data() if p[3])
    points, (w, h) = TAILS[pose]
    tail = [(x / w, y / h) for x, y in points]
    TAIL.update(split_zone(frame, tail, is_coat))
    TIP.update(split_zone(frame, tail, is_cream, step=2))  # set apart only so the mane skips it
    MANE.update(split_zone(frame, [(0, 0), (1, 0), (1, 1), (0, 1)], lambda c: is_cream(c) and c not in TIP))
    return frame


TAIL, MANE, TIP, ORIGINAL = set(), set(), set(), set()


def crop(img):
    return img.crop(img.getchannel("A").getbbox())


base = crop(remove_background(Image.open(HERE / "base.png")))
sheet = remove_background(Image.open(HERE / "poses.png"))
w, h = sheet.size
run_a, run_b, sleep, eat = (crop(sheet.crop((x, y, x + w // 2, y + h // 2)))
                            for y in (0, h // 2) for x in (0, w // 2))
# La hoja está dibujada a otra escala que base.png: se iguala por la anchura del zorro comiendo,
# que es la pose más parecida a estar de pie.
# ponytail: escala estimada a ojo por anchura; ajustar SHEET_FIX si una etapa se ve desproporcionada
SHEET_FIX = 1.0
k = eat.width / base.width * SHEET_FIX
base = base.resize((round(base.width * k), round(base.height * k)), Image.LANCZOS)
# En la hoja, el zorro dormido salió desproporcionadamente grande.
sleep = sleep.resize((round(sleep.width * 0.8), round(sleep.height * 0.8)), Image.LANCZOS)

shutil.rmtree(OUT, ignore_errors=True)
palette = set()
for stage, size in zip(STAGES, SIZES):
    small = pixelize_set([base, run_a, run_b, sleep, eat], size, COLORS)
    idle, ra, rb, sl, ea = (zones(f, pose) for f, pose in zip(small, TAILS))
    animations = {
        "idle": [idle, breathe(idle)],
        "active": [ra, rb],
        "sleep": [sl, breathe(sl, 0.5)],
        "eat": [ea, breathe(ea, 0.5)],
    }
    for name, frames in animations.items():
        folder = OUT / stage / name
        folder.mkdir(parents=True)
        for n, frame in enumerate(frames, start=1):
            frame.save(folder / f"{n:02}.png")
            palette |= {p[:3] for p in frame.get_flattened_data() if p[3]}

# Body coat: top language; tail: second; cream of the chest and cheeks (mane): third.
# The cream tip of the tail and the dark legs keep their colors.
hexes = lambda colors: sorted("#%02x%02x%02x" % c for c in colors & palette)
body = {c for c in palette if is_coat(c)} - TAIL
assert not (TAIL | MANE | TIP) & ORIGINAL, "a twin color matches an original one: change the step"
recolor = [hexes(body), hexes(TAIL), hexes(MANE)]
(OUT / "animal.json").write_text(json.dumps({"fps": FPS, "scale": 3, "recolor": recolor}, indent=2) + "\n")
print(f"{OUT}: palette {len(palette)} colors, groups {[len(g) for g in recolor]}")
