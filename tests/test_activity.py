"""Ejecutar con: python tests/test_activity.py"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image

from git_tracker.activity import summarize
from git_tracker.sprites import recolor

TODAY = date(2026, 11, 5)  # jueves; ayer = miércoles 4


def snapshot(counts, languages=()):
    """counts: contribuciones por día, terminando HOY (hoy se ignora por incompleto)."""
    start = TODAY - timedelta(days=len(counts) - 1)
    return {"days": [[(start + timedelta(days=i)).isoformat(), c] for i, c in enumerate(counts)],
            "languages": list(languages)}


s = summarize(snapshot([0] * 365), TODAY)
assert (s["stage"], s["animation"], s["quiet_days"]) == ("baby", "sleep", 364)

s = summarize(snapshot([1] * 100 + [0] * 10 + [9]), TODAY)  # el 9 es hoy: no cuenta
assert (s["stage"], s["animation"], s["quiet_days"]) == ("young", "idle", 10)

# primera contribución de la semana: lunes y martes a 0, miércoles (ayer) a 3
s = summarize(snapshot([1] * 300 + [0, 0, 3, 0]), TODAY)
assert (s["stage"], s["animation"]) == ("adult", "eat")

# semana muy por encima de la media
s = summarize(snapshot([0] * 300 + [2] * 7 + [0]), TODAY)
assert s["animation"] == "active", s

langs = [{"name": "Python", "color": "#3572A5"}, {"name": "Rust", "color": "#dea584"},
         {"name": "Python", "color": "#3572A5"}, {"name": "Shell", "color": None}]
s = summarize(snapshot([1] * 10, langs), TODAY, thresholds=(5, 8))
assert s["stage"] == "adult"
assert s["languages"] == ["Python", "Rust", "Shell"] and s["colors"] == ["#3572A5", "#dea584"]

# recolor: el gris del grupo toma el tono del lenguaje; lo demás no cambia
img = Image.new("RGBA", (2, 1))
img.putdata([(128, 128, 128, 255), (10, 20, 30, 255)])
out = recolor([img], [["#808080"]], ["#ff0000"])[0]
assert out.getpixel((0, 0)) == (128, 0, 0, 255) and out.getpixel((1, 0)) == (10, 20, 30, 255)

print("ok")
