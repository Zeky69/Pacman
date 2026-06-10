"""Lecture et écriture (robustes) du fichier de highscores.

Le format de référence sur disque est une liste JSON d'objets
``{"name": str, "score": int}``. Pour rester compatible avec d'anciens
fichiers, le format « dictionnaire » ``{"nom": score, ...}`` est aussi accepté
en lecture (il est migré vers le format liste au premier enregistrement).

Toute erreur (fichier absent, JSON cassé, format inattendu) est neutralisée :
la lecture renvoie une liste vide et l'affichage ne plante jamais.
"""

import json
from typing import Any


def _valid(name: Any, score: Any) -> bool:
    """Vrai si (name, score) est une entrée de score exploitable."""
    return (isinstance(name, str)
            and isinstance(score, int)
            and not isinstance(score, bool)
            and score >= 0)


def _normalize(data: Any) -> list[tuple[Any, Any]]:
    """Renvoie ``[(name, score), ...]`` depuis un format liste OU dict.

    - liste d'objets ``{"name": ..., "score": ...}`` (format de référence) ;
    - dict legacy ``{"nom": score, ...}``.
    Les entrées mal formées sont ignorées.
    """
    entries = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                name, score = item.get("name"), item.get("score")
                if _valid(name, score):
                    entries.append((name, score))
    elif isinstance(data, dict):
        for name, score in data.items():
            if _valid(name, score):
                entries.append((name, score))
    return entries


def _read(path: str) -> Any:
    """Charge le JSON brut du fichier, ou ``None`` en cas d'erreur."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def load_highscores(path: str, limit: int = 10) -> list[tuple[str, int]]:
    """Renvoie ``[(name, score), ...]`` trié par score décroissant.

    Les entrées mal formées sont ignorées. La liste est tronquée à `limit`.
    """
    entries = _normalize(_read(path))
    entries.sort(key=lambda e: e[1], reverse=True)
    return entries[:limit]


def save_highscore(path: str, name: str, score: int, limit: int = 100) -> list[tuple[str, int]]:
    """Ajoute ``(name, score)`` au fichier et le réécrit (format liste).

    Le fichier est lu, fusionné avec la nouvelle entrée, trié par score
    décroissant puis tronqué à `limit`. Renvoie la liste résultante.
    """
    name = (name or "").strip().upper()[:12] or "???"
    entries = _normalize(_read(path))
    entries.append((name, int(score)))
    entries.sort(key=lambda e: e[1], reverse=True)
    entries = entries[:limit]

    payload = [{"name": n, "score": s} for n, s in entries]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return entries
