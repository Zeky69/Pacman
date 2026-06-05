"""Chargement et validation du fichier de configuration (obligatoire).

Le jeu refuse de démarrer sans un `config.json` valide. Ce fichier définit
au minimum les dimensions du labyrinthe.
"""

import json
import sys

DEFAULT_CONFIG_PATH = "config.json"
REQUIRED_KEYS = ("width", "height")


def load_config(path=DEFAULT_CONFIG_PATH):
    """Lit et valide le fichier de config. Quitte le programme si invalide."""
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Erreur : fichier de configuration introuvable : '{path}'.\n"
                 f"Lance le jeu avec un config.json valide "
                 f"(ex: {{\"width\": 20, \"height\": 20}}).")
    except json.JSONDecodeError as e:
        sys.exit(f"Erreur : '{path}' n'est pas un JSON valide ({e}).")

    if not isinstance(config, dict):
        sys.exit(f"Erreur : '{path}' doit contenir un objet JSON.")

    for key in REQUIRED_KEYS:
        value = config.get(key)
        if not isinstance(value, int) or value <= 0:
            sys.exit(f"Erreur : la clé '{key}' de '{path}' doit être "
                     f"un entier positif (reçu : {value!r}).")

    return config
