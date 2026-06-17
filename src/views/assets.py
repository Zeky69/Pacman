"""Gestion des assets graphiques : manifeste + abstraction « skin ».

Sépare *quelle* animation jouer (défini par données dans
``assets/manifest.json``) de *d'où* viennent les pixels (planche par défaut
ou textures PNG d'un thème). Un ``Skin`` produit la liste de frames prêtes ;
l'``Animator`` ne fait plus que les rejouer.

Pipeline :
    Assets (lit le manifeste) -> Skin actif -> frames -> Animator
"""

import os
from typing import Any, Optional, Protocol
import pygame

from .sprites import SpriteSheet
from .sprite_view import Animator
from . import settings
from ..paths import resource_path

_Frames = tuple[list[pygame.Surface], str]


class Skin(Protocol):
    """Produit la liste de frames prêtes (transformées, mises à l'échelle) d'une animation."""

    def frames_for(self, anim: str, variant: str, size: int,
                   palette: tuple[int, int]) -> _Frames: ...


# Type d'une définition résolue : frames/fichiers, loop, flips, rotation.
_Resolved = tuple[list[Any], Optional[str], bool, bool, int]


def _resolve(table: dict[str, Any], name: str, frames_key: str) -> _Resolved:
    """Résout une entrée d'animation/override, en suivant ``from``.

    Règle uniforme : ``from`` n'hérite que des *frames* et du *loop* (pour ne
    pas redéfinir la liste à chaque direction) ; la transformation
    (flip/rotation) est toujours propre à l'entrée, défaut neutre. Le ``loop``
    vaut ``None`` s'il n'est pas spécifié, laissant l'appelant choisir un défaut.
    """
    entry = table[name]
    if "from" in entry:
        frames, loop, _, _, _ = _resolve(table, entry["from"], frames_key)
        if "loop" in entry:
            loop = entry["loop"]
    else:
        frames = entry[frames_key]
        loop = entry.get("loop")
    return (frames, loop,
            entry.get("x_flip", False),
            entry.get("y_flip", False),
            entry.get("rotation", 0))


def _finalize(raw: list[pygame.Surface], x_flip: bool, y_flip: bool,
              rotation: int, size: int, loop_type: str) -> list[pygame.Surface]:
    """Applique flip/rotation, met à la taille ``size`` et déplie le pingpong.

    ``scale`` (plus proche voisin) garde des pixels nets. En pingpong, on
    rejoue les frames intermédiaires à l'envers.
    """
    frames = []
    for img in raw:
        if x_flip or y_flip:
            img = pygame.transform.flip(img, x_flip, y_flip)
        if rotation:
            img = pygame.transform.rotate(img, rotation)
        frames.append(pygame.transform.scale(img, (size, size)))
    if loop_type == "pingpong" and len(frames) > 2:
        frames += [frames[i] for i in range(len(frames) - 2, 0, -1)]
    return frames


class PngFolder:
    """Dossier de textures PNG individuelles, chargées à la demande et cachées."""

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self._cache: dict[str, Optional[pygame.Surface]] = {}

    def load(self, name: str) -> Optional[pygame.Surface]:
        if name not in self._cache:
            path = os.path.join(self.directory, name)
            try:
                self._cache[name] = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError, OSError):
                print(f"Avertissement : texture introuvable « {path} » "
                      f"— fallback sur la planche par défaut.")
                self._cache[name] = None
        return self._cache[name]


class SheetSkin:
    """Skin par défaut : les frames sont extraites de la planche de sprites."""

    def __init__(self, sheet: SpriteSheet, animations: dict[str, Any]) -> None:
        self.sheet = sheet
        self.animations = animations

    def frames_for(self, anim: str, variant: str, size: int,
                   palette: tuple[int, int]) -> _Frames:
        adef = self.animations[anim]
        coords, loop, xf, yf, rot = _resolve(adef["variants"], variant, "frames")
        loop = loop or "none"
        getter = (self.sheet.get_large_sprite if adef.get("size") == "large"
                  else self.sheet.get_small_sprite)
        pi, mr = palette
        raw = [getter(mr, pi, c, r, 1) for c, r in coords]
        return _finalize(raw, xf, yf, rot, size, loop), loop


class OverlaySkin:
    """Skin de thème : remplace certaines animations par des PNG dédiés.

    Le fallback se fait *au niveau de l'animation entière* : si un seul PNG
    manque pour une animation, on retombe sur le skin de base — jamais un
    mélange PNG / planche frame par frame.
    """

    def __init__(self, base: Skin, png: PngFolder,
                 overrides: dict[str, Any], animations: dict[str, Any]) -> None:
        self.base = base
        self.png = png
        self.overrides = overrides
        self.animations = animations

    def frames_for(self, anim: str, variant: str, size: int,
                   palette: tuple[int, int]) -> _Frames:
        key = f"{anim}/{variant}"
        if key in self.overrides:
            files, ov_loop, xf, yf, rot = _resolve(self.overrides, key, "files")
            raw = [self.png.load(f) for f in files]
            if all(img is not None for img in raw):
                # Loop : celui de l'override, sinon celui de l'animation source.
                _, anim_loop, _, _, _ = _resolve(
                    self.animations[anim]["variants"], variant, "frames")
                loop = ov_loop or anim_loop or "none"
                return _finalize(raw, xf, yf, rot, size, loop), loop  # type: ignore[arg-type]
        return self.base.frames_for(anim, variant, size, palette)


class Assets:
    """Point d'entrée : charge le manifeste, choisit le skin, produit les animateurs."""

    def __init__(self, secret: bool = False,
                 manifest: Optional[dict[str, Any]] = None) -> None:
        if manifest is None:
            manifest = settings.MANIFEST
        self.sheet = SpriteSheet(resource_path(manifest["sheet"]["path"]))
        self.animations: dict[str, Any] = manifest["animations"]
        base = SheetSkin(self.sheet, self.animations)
        skin_def = manifest.get("skins", {}).get("secret" if secret else "default", {})
        if secret and skin_def.get("overrides"):
            png = PngFolder(resource_path(skin_def["dir"]))
            self.skin: Skin = OverlaySkin(
                base, png, skin_def["overrides"], self.animations)
        else:
            self.skin = base

    def _palette(self, anim: str,
                 override: Optional[tuple[int, int]]) -> tuple[int, int]:
        if override is not None:
            return override
        palette = self.animations[anim].get("palette", (0, 0))
        return (palette[0], palette[1])

    def states(self, anim: str) -> dict[str, Any]:
        """Descriptions d'états (variante + couleur) d'une entité, depuis le manifeste.

        Ex. pour `ghost` : `normal` / `eaten` / `frightened`, chacun précisant
        la variante à jouer et la palette à appliquer (couleur de l'entité,
        couleur fixe, et éventuelle couleur de clignotement).
        """
        states: dict[str, Any] = self.animations[anim].get("states", {})
        return states

    def animator(self, anim: str, variant: str, size: int,
                 palette: Optional[tuple[int, int]] = None,
                 speed: int = 100) -> Animator:
        frames, loop = self.skin.frames_for(
            anim, variant, size, self._palette(anim, palette))
        return Animator(frames, loop, speed)

    def sprite(self, anim: str, variant: str, size: int,
               palette: Optional[tuple[int, int]] = None) -> pygame.Surface:
        """Sprite statique (1re frame) via le skin actif — gommes, icône de vie…"""
        frames, _ = self.skin.frames_for(
            anim, variant, size, self._palette(anim, palette))
        return frames[0]

    def life_icon_source(self, size: int) -> pygame.Surface:
        """Première frame de Pac-Man (skin actif), pour l'icône de vie du HUD."""
        return self.sprite("pacman", "right", size)
