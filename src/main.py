"""Point d'entrée du jeu Pac-Man.

Lancement : uv run pac-man.py [config.json]
Un fichier de configuration peut être passé en argument. Sans argument (cas du
double-clic sur l'exécutable empaqueté), le ``config.json`` embarqué est utilisé.
"""

import os
import sys

from .config import DEFAULT_CONFIG_PATH, load_config
from .paths import app_dir, resource_path
from .controllers.game_controller import GameController


def _default_config_path() -> str:
    """Config à utiliser quand aucun argument n'est passé (double-clic).

    On privilégie un ``config.json`` posé à côté de l'exécutable : il est
    éditable après build, donc on peut changer les réglages — ou le remplacer
    par un autre fichier — sans recompiler. À défaut, on retombe sur le
    config.json embarqué (toujours présent, en lecture seule).
    """
    external = os.path.join(app_dir(), DEFAULT_CONFIG_PATH)
    return external if os.path.isfile(external) else resource_path(DEFAULT_CONFIG_PATH)


def main() -> None:
    if len(sys.argv) > 2:
        prog = sys.argv[0] if sys.argv else "pac-man.py"
        sys.exit(f"Usage : {prog} [config.json]\n"
                 f"Au plus un fichier de configuration est attendu.")
    # Argument explicite = chemin fourni par l'utilisateur ; sinon, config par défaut.
    config_path = sys.argv[1] if len(sys.argv) == 2 else _default_config_path()
    config = load_config(config_path)
    GameController(config).run()


if __name__ == "__main__":
    main()
