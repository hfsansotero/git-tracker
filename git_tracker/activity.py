"""Recogida de actividad pública en GitHub y su traducción a etapa, animación y colores."""
import json
import os
import urllib.request
from bisect import bisect_right
from collections import Counter
from datetime import date, timedelta

from git_tracker.sprites import STAGES

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { primaryLanguage { name color } }
    }
  }
}
"""
SLEEP_QUIET_DAYS = 14
# growth: días de la ventana móvil que decide el tamaño, y umbrales por defecto (young, adult)
GROWTH_DAYS = {"week": 7, "month": 30, "year": 365}
GROWTH_THRESHOLDS = {"week": (2, 8), "month": (5, 25), "year": (50, 300)}
# mood: mínimo de contribuciones para "active", aunque tu media sea muy baja
ACTIVE_MIN = {"day": 5, "week": 5, "month": 10}


def collect(login: str, token: str | None = None) -> dict:
    """Último año de contribuciones y lenguaje principal de los repos públicos propios."""
    # ponytail: solo los 100 repos con push más reciente; paginar si hiciera falta
    token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing token: set GITHUB_TOKEN (locally: export GITHUB_TOKEN=$(gh auth token))")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "git-tracker"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if data.get("errors"):
        raise SystemExit(f"GitHub API: {data['errors'][0]['message']}")
    user = data["data"]["user"]
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {
        "login": login,
        "days": [[d["date"], d["contributionCount"]] for w in weeks for d in w["contributionDays"]],
        "languages": [r["primaryLanguage"] for r in user["repositories"]["nodes"] if r["primaryLanguage"]],
    }


def _period_totals(days: list, today: date, mood: str) -> list[int]:
    """Totales de cada semana (lunes-domingo) o mes natural ya terminados, del más antiguo
    al más reciente. Se descarta el primero, que casi siempre está incompleto."""
    key = (lambda d: d - timedelta(days=d.weekday())) if mood == "week" else (lambda d: (d.year, d.month))
    totals: dict = {}
    for d, c in days:
        totals[key(d)] = totals.get(key(d), 0) + c
    totals.pop(key(today), None)  # el periodo en curso aún no ha terminado
    return list(totals.values())[1:]


def _mood_period(totals: list[int], mood: str) -> str:
    """La última semana o mes terminado, comparado con los anteriores."""
    if not totals:
        return "idle"
    last, history = totals[-1], totals[:-1]
    average = sum(history) / len(history) if history else 0
    if last == 0:
        return "sleep"
    if history and history[-1] == 0:
        return "eat"
    if last >= max(ACTIVE_MIN[mood], 2 * average):
        return "active"
    return "idle"


def summarize(snapshot: dict, today: date, growth: str = "year", mood: str = "day",
              thresholds=None) -> dict:
    """Etapa, animación y colores. Hoy no cuenta: el día aún no ha terminado.

    growth (tamaño): contribuciones de los últimos 7 / 30 / 365 días frente a `thresholds`
    (por defecto GROWTH_THRESHOLDS[growth]).

    mood (animación), gana la primera regla que se cumpla:

    | animación | mood=day                                   | mood=week / month                         |
    | sleep     | SLEEP_QUIET_DAYS o más días sin contribuir | la última semana/mes terminado vacío      |
    | eat       | ayer fue el primer día con contribuciones  | volviste tras una semana/mes vacío        |
    |           | de su semana (lunes-domingo)               |                                           |
    | active    | últimos 7 días >= 2x tu media semanal      | la última semana/mes >= 2x tu media        |
    | idle      | cualquier otro caso                        | cualquier otro caso                       |

    `active` además exige un mínimo (ACTIVE_MIN) para que una media muy baja no lo dispare.
    """
    thresholds = list(thresholds or GROWTH_THRESHOLDS[growth])
    days = [(date.fromisoformat(d), c) for d, c in snapshot["days"] if date.fromisoformat(d) < today]
    counts = [c for _, c in days]
    window_start = today - timedelta(days=GROWTH_DAYS[growth])
    grown = sum(c for d, c in days if d >= window_start)

    if mood == "day":
        quiet = next((i for i, c in enumerate(reversed(counts)) if c), len(counts))
        yesterday = days[-1][0] if days else today - timedelta(days=1)
        monday = yesterday - timedelta(days=yesterday.weekday())
        week = [c for d, c in days if d >= monday]
        last = sum(counts[-7:])
        if quiet >= SLEEP_QUIET_DAYS:
            animation = "sleep"
        elif week and week[-1] > 0 and not any(week[:-1]):
            animation = "eat"
        elif last >= max(ACTIVE_MIN["day"], 2 * sum(counts[-365:]) / 52):
            animation = "active"
        else:
            animation = "idle"
    else:
        totals = _period_totals(days, today, mood)
        animation = _mood_period(totals, mood)
        last = totals[-1] if totals else 0

    languages = Counter(l["name"] for l in snapshot["languages"])
    color = {l["name"]: l["color"] for l in snapshot["languages"]}
    top = [name for name, _ in languages.most_common()]
    return {
        "stage": STAGES[bisect_right(thresholds, grown)],
        "animation": animation,
        "growth": growth,
        "growth_contributions": grown,
        "thresholds": thresholds,
        "mood": mood,
        "mood_contributions": last,  # day: últimos 7 días; week/month: el último periodo terminado
        "languages": top,
        "colors": [color[name] for name in top if color[name]],
    }
