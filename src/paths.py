"""Résolution des chemins de fichiers, compatible exécutable PyInstaller.

En développement, les ressources (assets, config) vivent à la racine du projet
et le fichier de scores est écrit à côté. Une fois le jeu empaqueté par
PyInstaller, les ressources embarquées sont extraites dans un dossier
temporaire en *lecture seule* (``sys._MEIPASS``) : il faut donc résoudre les
ressources via ce dossier, mais écrire les fichiers modifiables (les scores)
ailleurs, dans un dossier de données utilisateur.

Deux fonctions, deux usages :
  - ``resource_path``  : lire une ressource embarquée (manifeste, PNG, config) ;
  - ``user_data_path`` : lire/écrire un fichier modifiable (scores).
"""

import os
import sys


def _frozen() -> bool:
    """Vrai si le code tourne depuis un exécutable PyInstaller."""
    return getattr(sys, "frozen", False)


def _project_root() -> str:
    """Racine du projet en développement (le dossier parent de ``src``)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def app_dir() -> str:
    """Dossier où l'utilisateur peut déposer des fichiers à côté du programme.

    En exécutable PyInstaller, c'est le dossier qui *contient* l'exécutable
    (``dist/pacman/``) — visible et éditable, contrairement aux ressources
    embarquées en lecture seule. En développement, c'est la racine du projet.
    Sert à chercher un ``config.json`` modifiable sans recompiler.
    """
    if _frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return _project_root()


def resource_path(relative: str) -> str:
    """Chemin absolu d'une ressource *embarquée* (lecture seule).

    En exécutable PyInstaller, la base est le dossier d'extraction temporaire
    (``sys._MEIPASS``) ; en développement, c'est la racine du projet. Le chemin
    ``relative`` est toujours exprimé tel qu'il l'est dans le code source
    (p. ex. ``"assets/manifest.json"``).
    """
    if _frozen():
        base = getattr(sys, "_MEIPASS", _project_root())
    else:
        base = _project_root()
    return os.path.join(base, relative)


def user_data_path(filename: str) -> str:
    """Chemin absolu d'un fichier *inscriptible*, son dossier étant créé au besoin.

    Le bundle PyInstaller est en lecture seule : on range donc les fichiers
    modifiables (scores) dans un dossier de données utilisateur stable, propre à
    la plateforme. En développement, on garde le fichier à la racine du projet
    pour ne rien changer au flux de travail habituel. Seul le nom de fichier est
    conservé (un éventuel chemin fourni par la config est ignoré).
    """
    if _frozen():
        if sys.platform == "win32":
            root = os.environ.get("APPDATA") or os.path.expanduser("~")
        elif sys.platform == "darwin":
            root = os.path.expanduser("~/Library/Application Support")
        else:
            root = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        directory = os.path.join(root, "pacman")
    else:
        directory = _project_root()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, os.path.basename(filename))
