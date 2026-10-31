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


# --- mood=day (por defecto) y growth=year (por defecto)
s = summarize(snapshot([0] * 365), TODAY)
assert (s["stage"], s["animation"], s["growth_contributions"]) == ("baby", "sleep", 0)

s = summarize(snapshot([1] * 100 + [0] * 10 + [9]), TODAY)  # el 9 es hoy: no cuenta
assert (s["stage"], s["animation"], s["growth_contributions"]) == ("young", "idle", 100)

# primera contribución de la semana: lunes y martes a 0, miércoles (ayer) a 3
s = summarize(snapshot([1] * 300 + [0, 0, 3, 0]), TODAY)
assert (s["stage"], s["animation"]) == ("adult", "eat")

# semana muy por encima de la media
s = summarize(snapshot([0] * 300 + [2] * 7 + [0]), TODAY)
assert s["animation"] == "active", s

# --- growth: misma actividad (1 al día), distinta ventana y umbrales por defecto
daily = snapshot([1] * 100 + [0])
assert summarize(daily, TODAY, growth="week")["growth_contributions"] == 7
assert summarize(daily, TODAY, growth="week")["stage"] == "young"   # 7: entre 2 y 8
assert summarize(daily, TODAY, growth="month")["stage"] == "adult"  # 30 >= 25
assert summarize(daily, TODAY, growth="year")["stage"] == "young"   # 100: entre 50 y 300
assert summarize(daily, TODAY, growth="month", thresholds=(40, 90))["stage"] == "baby"

# --- mood=week: hoy es jueves 5; la última semana terminada es lun 26 oct - dom 1 nov
#     (posiciones -11..-5 de la lista); la semana en curso (-4..-1) no cuenta
week = lambda counts: summarize(snapshot(counts), TODAY, mood="week")
assert week([1] * 100 + [0] * 7 + [3, 3, 3, 0])["animation"] == "sleep"
assert week([1] * 93 + [0] * 7 + [1] * 7 + [0] * 4)["animation"] == "eat"
s = week([1] * 100 + [5] * 7 + [0] * 4)
assert (s["animation"], s["mood_contributions"]) == ("active", 35)
assert week([1] * 111)["animation"] == "idle"

# --- mood=month: el último mes terminado es octubre (posiciones -36..-6)
month = lambda counts: summarize(snapshot(counts), TODAY, mood="month")
assert month([1] * 100 + [0] * 31 + [1] * 5)["animation"] == "sleep"
assert month([1] * 100 + [3] * 31 + [0] * 5)["animation"] == "active"
assert month([1] * 136)["animation"] == "idle"
assert month([0] * 5)["animation"] == "idle"  # cuenta nueva, sin meses terminados

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
