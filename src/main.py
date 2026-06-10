"""Point d'entrée du jeu Pac-Man.

Lancement : uv run pac-man.py [config.json]
Un fichier de configuration valide est obligatoire (voir src/config.py).
"""

import sys

from .config import load_config
from .controllers.game_controller import GameController


def main() -> None:
    if len(sys.argv) != 2:
        prog = sys.argv[0] if sys.argv else "pac-man.py"
        sys.exit(f"Usage : uv run {prog} <config.json>\n"
                 f"Un fichier de configuration est obligatoire.")
    config = load_config(sys.argv[1])
    GameController(config).run()


if __name__ == "__main__":
    main()
