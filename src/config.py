"""Chargement, nettoyage et validation du fichier de configuration.

Le jeu prend exactement un argument : un fichier JSON. En plus du JSON
standard, les lignes de commentaire (commençant par ``#`` ou ``//``) sont
ignorées avant le parsing.

Politique de robustesse (exigée par le sujet) :
  - Fichier introuvable / illisible / JSON invalide / racine non-objet :
    erreur fatale mais *propre* (message clair, jamais de traceback Python).
  - Valeur invalide : on log un avertissement et on ramène la clé à un
    défaut sûr (« clamp »), puis on continue.
  - Clé absente : on utilise le défaut silencieusement.
  - Clé inconnue : ignorée.
"""

import json
import sys
from typing import Any

from .paths import user_data_path

DEFAULT_CONFIG_PATH = "config.json"

# Valeurs par défaut sûres pour chaque clé connue.
DEFAULTS = {
    "highscore_filename": "scoreboard.json",
    "width": 20,
    "height": 20,
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "level_count": 5,
    "pacman_speed": 1.0,
    "ghost_speed": 1.0,
    "invincible": False,
    "secret": False,
}

# Catégories de validation.
_BOOL_KEYS = ("invincible", "secret")
_STRING_KEYS = ("highscore_filename",)
# Entier >= 0 toléré (un score nul ou une graine 0 sont valides).
_NON_NEGATIVE_INT_KEYS = (
    "points_per_pacgum", "points_per_super_pacgum",
    "points_per_ghost", "seed",
)
# Vitesses : nombre (int ou float) strictement positif.
_POSITIVE_FLOAT_KEYS = ("pacman_speed", "ghost_speed")
# Toutes les autres clés numériques exigent un entier strictement positif.

# Bornes (min, max) pour les clés à intervalle restreint. Une valeur entière
# valide mais hors bornes est ramenée dans l'intervalle (« clamp ») plutôt que
# de planter : un labyrinthe trop grand ferait exploser la mémoire (la surface
# pygame du labyrinthe est dimensionnée sur width/height).
_RANGES = {
    "width": (5, 35),
    "height": (5, 35),
}


def _strip_comments(text: str) -> str:
    """Retire les lignes de commentaire (# ou //) avant le parsing JSON.

    Seules les lignes dont le premier caractère non blanc est ``#`` ou
    ``//`` sont supprimées : un ``#`` à l'intérieur d'une valeur chaîne
    n'est donc jamais affecté.
    """
    kept = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _validate(key: str, value: Any) -> Any:
    """Renvoie la valeur normalisée si elle est valide, sinon None.

    En Python ``bool`` est un sous-type de ``int`` : on le refuse
    explicitement pour éviter qu'un ``true`` ne passe pour un entier.
    """
    if key in _BOOL_KEYS:
        return value if isinstance(value, bool) else None
    if isinstance(value, bool):
        return None
    if key in _STRING_KEYS:
        return value if isinstance(value, str) and value.strip() else None
    if key in _POSITIVE_FLOAT_KEYS:
        return value if isinstance(value, (int, float)) and value > 0 else None
    if key in _NON_NEGATIVE_INT_KEYS:
        return value if isinstance(value, int) and value >= 0 else None
    return value if isinstance(value, int) and value > 0 else None


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Construit une config complète depuis les défauts et les valeurs lues.

    Chaque clé connue est validée puis clampée si besoin. Les clés inconnues
    présentes dans `data` sont ignorées.
    """
    config = dict(DEFAULTS)
    for key, default in DEFAULTS.items():
        if key not in data:
            continue
        valid = _validate(key, data[key])
        if valid is None:
            print(f"Config: invalid value for '{key}' "
                  f"({data[key]!r}) — using default {default!r}.",
                  file=sys.stderr)
        else:
            config[key] = _clamp(key, valid)
    return config


def _clamp(key: str, value: Any) -> Any:
    """Ramène `value` dans l'intervalle autorisé de `key` (si défini).

    Les valeurs hors bornes (ex. un labyrinthe gigantesque) sont ramenées au
    min/max au lieu de planter le jeu. Un avertissement est affiché.
    """
    bounds = _RANGES.get(key)
    if bounds is None:
        return value
    low, high = bounds
    clamped = max(low, min(value, high))
    if clamped != value:
        print(f"Config: '{key}' value {value!r} out of range "
              f"[{low}, {high}] — clamped to {clamped!r}.",
              file=sys.stderr)
    return clamped


def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Lit, nettoie et valide le fichier de config ; renvoie un dict complet.

    Quitte proprement (message clair, sans traceback) si le fichier est
    introuvable, illisible, n'est pas un JSON valide ou ne contient pas un
    objet JSON.
    """
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        sys.exit(f"Error: cannot read configuration file '{path}' ({e}).")

    try:
        data = json.loads(_strip_comments(raw))
    except json.JSONDecodeError as e:
        sys.exit(f"Error: '{path}' is not valid JSON ({e}).")

    if not isinstance(data, dict):
        sys.exit(f"Error: '{path}' must contain a JSON object "
                 f"(e.g. {{\"width\": 20, \"height\": 20}}).")

    config = _normalize(data)
    # Le bundle PyInstaller étant en lecture seule, on redirige le fichier de
    # scores vers un dossier de données utilisateur inscriptible (no-op en dev).
    config["highscore_filename"] = user_data_path(config["highscore_filename"])
    return config
