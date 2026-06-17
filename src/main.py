"""Point d'entrée du jeu Pac-Man.

Lancement : uv run pac-man.py [config.json]
Un fichier de configuration peut être passé en argument. Sans argument (cas du
double-clic sur l'exécutable empaqueté), le ``config.json`` embarqué est utilisé.
"""

import sys

from .config import load_config
from .paths import resource_path
from .controllers.game_controller import GameController


def main() -> None:
    if len(sys.argv) > 2:
        prog = sys.argv[0] if sys.argv else "pac-man.py"
        sys.exit(f"Usage : {prog} [config.json]\n"
                 f"Au plus un fichier de configuration est attendu.")
    # Argument explicite = chemin fourni par l'utilisateur ; sinon, on retombe
    # sur le config.json embarqué (indispensable pour un lancement par double-clic).
    config_path = sys.argv[1] if len(sys.argv) == 2 else resource_path("config.json")
    config = load_config(config_path)
    GameController(config).run()


if __name__ == "__main__":
    main()
