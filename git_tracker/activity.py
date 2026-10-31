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
ACTIVE_MIN_WEEK = 5  # una semana "activa" necesita al menos esto, aunque la media sea muy baja


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


def summarize(snapshot: dict, today: date, thresholds=(50, 300)) -> dict:
    """Etapa por contribuciones del último año; animación por lo que pasó hasta ayer:

    | animación | cuándo (gana la primera)                                       |
    | sleep     | SLEEP_QUIET_DAYS o más días seguidos sin contribuir            |
    | eat       | ayer fue el primer día con contribuciones de su semana (L-D)   |
    | active    | últimos 7 días >= el doble de la media semanal (y >= 5)        |
    | idle      | cualquier otro caso                                            |
    """
    days = [(date.fromisoformat(d), c) for d, c in snapshot["days"] if date.fromisoformat(d) < today]
    counts = [c for _, c in days]
    total = sum(counts)
    last7 = sum(counts[-7:])
    quiet = next((i for i, c in enumerate(reversed(counts)) if c), len(counts))

    yesterday = days[-1][0] if days else today - timedelta(days=1)
    monday = yesterday - timedelta(days=yesterday.weekday())
    week = [c for d, c in days if d >= monday]
    first_of_week = bool(week) and week[-1] > 0 and not any(week[:-1])

    if quiet >= SLEEP_QUIET_DAYS:
        animation = "sleep"
    elif first_of_week:
        animation = "eat"
    elif last7 >= max(ACTIVE_MIN_WEEK, 2 * total / 52):
        animation = "active"
    else:
        animation = "idle"

    languages = Counter(l["name"] for l in snapshot["languages"])
    color = {l["name"]: l["color"] for l in snapshot["languages"]}
    top = [name for name, _ in languages.most_common()]
    return {
        "stage": STAGES[bisect_right(list(thresholds), total)],
        "animation": animation,
        "contributions_last_year": total,
        "contributions_last_7_days": last7,
        "quiet_days": quiet,
        "languages": top,
        "colors": [color[name] for name in top if color[name]],
    }
