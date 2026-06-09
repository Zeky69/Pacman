"""Lecture (robuste) du fichier de highscores.

Le format sur disque est une liste JSON d'objets ``{"name": str,
"score": int}``. Toute erreur (fichier absent, JSON cassé, format inattendu)
renvoie une liste vide : l'affichage ne plante jamais.
"""

import json


def load_highscores(path, limit=10):
    """Renvoie ``[(name, score), ...]`` trié par score décroissant.

    Les entrées mal formées sont ignorées. La liste est tronquée à `limit`.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []

    entries = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        score = item.get("score")
        if (isinstance(name, str)
                and isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0):
            entries.append((name, score))

    entries.sort(key=lambda e: e[1], reverse=True)
    return entries[:limit]
