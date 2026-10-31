"""Ejecutar con: python tests/test_sprites.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image

from git_tracker import sprites


def frame(path: Path, size, color=(255, 0, 0, 255)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, color).save(path)


with tempfile.TemporaryDirectory() as tmp:
    animal = Path(tmp) / "test"
    frame(animal / "baby/idle/1.png", (8, 8))
    frame(animal / "adult/idle/2.png", (16, 12))
    frame(animal / "adult/idle/10.png", (16, 12), (0, 0, 255, 255))
    frame(animal / "adult/sleep/01.png", (16, 10))

    # orden natural: 2 antes que 10
    used, frames = sprites.find_frames(animal, "adult", "idle")
    assert frames[1].getpixel((0, 0)) == (0, 0, 255, 255)
    # animación que falta -> idle de la misma etapa
    assert sprites.find_frames(animal, "baby", "sleep")[0] == animal / "baby/idle"
    # etapa que falta -> la más cercana, la menor si empatan
    assert sprites.find_frames(animal, "young", "sleep")[0] == animal / "baby/idle"
    assert sprites.find_frames(animal, "adult", "sleep")[0] == animal / "adult/sleep"

    canvas = sprites.canvas_size(animal)
    assert canvas == (16, 12)
    assert sprites.palette(animal) == {"#ff0000": 8 * 8 + 16 * 12 + 16 * 10, "#0000ff": 16 * 12}
    out = sprites.compose(frames, canvas, 2)
    assert out[0].size == (32, 24)
    small = sprites.compose([Image.new("RGBA", (8, 8), (255, 0, 0, 255))], canvas, 1)[0]
    assert small.getpixel((4, 11))[3] == 255 and small.getpixel((4, 0))[3] == 0  # apoyado abajo y centrado
    sprites.save_gif(out, Path(tmp) / "a.gif", 6)
    assert sprites.fps_for({"fps": {"idle": 2}}, "idle") == 2 and sprites.fps_for({"fps": {"idle": 2}}, "eat") == 6
    assert sprites.fps_for({"fps": 3}, "eat") == 3

    src = Path(tmp) / "src.png"
    img = Image.new("RGB", (200, 100), (230, 230, 235))  # fondo liso sin transparencia
    img.paste((10, 200, 30), (20, 25, 180, 75))  # figura de 160x50
    img.paste((230, 230, 235), (90, 40, 110, 60))  # hueco interior del color del fondo: no se borra
    img.save(src)
    sprites.make_animal(src, Path(tmp) / "custom")
    adult = Image.open(Path(tmp) / "custom/adult/idle/01.png")
    assert adult.size == (26, 9), adult.size  # 160x50 * 32/200 = 26x8, +1 fila del bote
    assert adult.getpixel((13, 4))[3] == 255  # el hueco interior sigue opaco
    baby = Image.open(Path(tmp) / "custom/baby/idle/02.png")
    assert baby.size[1] == 5 and 12 <= baby.size[0] <= 14, baby.size  # bordes suavizados: ±1 px

    # paleta común: el mismo color sale idéntico en dos frames de distinto tamaño
    a = Image.new("RGBA", (40, 40), (200, 90, 40, 255))
    b = Image.new("RGBA", (20, 20), (200, 90, 40, 255))
    fa, fb = sprites.pixelize_set([a, b], 20)
    assert fa.size == (20, 20) and fb.size == (10, 10) and fa.getpixel((0, 0)) == fb.getpixel((0, 0))
    assert sprites.breathe(fa, 0.5).getpixel((0, 0))[3] == 0  # la parte de arriba baja 1 px

print("ok")
