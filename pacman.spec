# -*- mode: python ; coding: utf-8 -*-
"""Recette d'empaquetage PyInstaller du jeu Pac-Man.

Construit un exécutable autonome (Python + pygame + assets embarqués) prêt à
être déposé sur itch.io. Compilation par plateforme :

    uv run pyinstaller pacman.spec

Le résultat est dans ``dist/pacman/`` (dossier à zipper et uploader).
"""

# Ressources embarquées : (source sur disque, dossier cible dans le bundle).
# Elles sont résolues à l'exécution via src/paths.py (sys._MEIPASS).
datas = [
    ("assets", "assets"),
    ("config.json", "."),
]

a = Analysis(
    ["pac-man.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["mazegenerator"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["flake8", "mypy", "tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # pas de console derrière la fenêtre du jeu
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="pacman",
)
