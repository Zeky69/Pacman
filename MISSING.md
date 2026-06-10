# Audit — ce qui manque par rapport au sujet

> Basé sur `en.subject.pdf` v1.4 et l'état actuel du dépôt (branche `master`, 10 juin 2026).

---

## ✅ Corrigé

| # | Problème | Correction apportée |
|---|----------|---------------------|
| 1 | Cible `debug` manquante dans le Makefile | Ajoutée : `uv run python -m pdb pac-man.py config.json` |
| 2 | Flags `mypy` manquants dans `lint` | Les 5 flags exigés ajoutés au Makefile |
| 3 | `DEFAULT_LEVEL_COUNT = 5` < 10 | Passé à `10` dans `game.py` ; `config.json` surcharge à `5` |
| 6 | README documentait `godmode` au lieu de `invincible` | Clé corrigée dans le tableau de configuration |
| 7 | Lien vers le répertoire de gestion de projet absent | Lien ajouté dans la section *Project Management* du README |

---

## Problèmes restants (action requise)

### 4. Aucun déploiement sur plateforme publique *(Chapter VII — critique)*

Le sujet exige :
- Un build **fonctionnel** sur Steam, Itch.io ou équivalent (public mais unlisted/privé).
- Un **script / spec de packaging** à la racine du dépôt (ex. spec PyInstaller, `build.sh`).
- Des instructions minimales in-package (contrôles, options, config).

**Rien de tout cela n'existe dans le dépôt.**

---

## Mineur restant

### 8. `.gitignore` exclut `uv.lock` via `*.lock`

`uv.lock` est commité mais `.gitignore` contient `*.lock`.  
Git ignorera toute modification future du lockfile → les dépendances peuvent diverger silencieusement.

**Correction :** remplacer `*.lock` par les patterns voulus ou ajouter `!uv.lock`.
