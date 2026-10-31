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

from git_tracker.sprites import STAGES, breathe, pixelize_set, remove_background

HERE = Path(__file__).parent
OUT = HERE.parents[1] / "animals" / "fox"
SIZES = (36, 50, 64)  # lado mayor del frame más grande en cada etapa
COLORS = 14
FPS = {"idle": 1.33, "active": 4, "sleep": 0.8, "eat": 2.67}


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
    idle, ra, rb, sl, ea = pixelize_set([base, run_a, run_b, sleep, eat], size, COLORS)
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

# El pelaje naranja toma el color del lenguaje principal; crema y patas oscuras se quedan.
coat = sorted(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette
              if (lambda hh, s, v: hh < 0.12 and s > 0.45 and v > 0.35)(*colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)))
(OUT / "animal.json").write_text(json.dumps({"fps": FPS, "scale": 3, "recolor": [coat]}, indent=2) + "\n")
print(f"{OUT}: palette {len(palette)} colors, coat {coat}")
