# Project Management — Pac-Man (42 Curriculum)

**Team:** zakburak (Zeky69 / Zekeriya) · elsahin (thorfinn / spectre)  
**Period:** 2026-05-25 → 2026-06-17  
**Repository:** https://github.com/Zeky69/Pacman

---

## 1. Team Organisation

| Member | GitHub handle | Role |
|--------|--------------|------|
| zakburak | Zeky69 / Zekeriya | Core engine, ghost AI, game mechanics, fruit system, asset manifest, secret mode, cheat mode, debug tools |
| elsahin | thorfinn / spectre | Config validation, UI scenes, HUD, mouse navigation, maze view refactor, font scaling |

**Decision process:** async via GitHub commits + direct communication. No formal meetings recorded. Conflicts resolved by the author of the affected module.

**Issue handling:** bugs were fixed directly in follow-up commits on the same day they were introduced (visible from git log).

---

## 2. Timeline (extracted from git history)

### Phase 1 — Research & Prototype (2026-05-25 → 2026-05-30)

| Date | Author | Activity |
|------|--------|----------|
| 2026-05-25 | zakburak | Design spec for grid debugger / zoom-pan tool |
| 2026-05-29 | zakburak | Initial maze tile placement and texture testing |
| 2026-05-30 | zakburak | Maze grid auto-tiling logic; default sprite asset |

**Goal:** validate the tile-based rendering approach and the external maze generator interface before building the full engine.

---

### Phase 2 — Core Engine (2026-05-30 → 2026-06-07)

| Date | Author | Activity |
|------|--------|----------|
| 2026-06-03 | zakburak | Fix asset paths and colour indices |
| 2026-06-05 | zakburak | **Major refactor:** full MVC structure (controllers / models / views), config loading, maze generation, sprite animation, Pac-Man + ghost entities, game loop |
| 2026-06-05 | zakburak | Ghost spawn directions and default colour fix |
| 2026-06-07 | zakburak | Fullscreen mode, improved ghost/Pac-Man movement, new maze elements |

**Goal:** establish the architecture (MVC + scene system) and a playable first version.

---

### Phase 3 — Ghost AI & Game Mechanics (2026-06-08 → 2026-06-09)

| Date | Author | Activity |
|------|--------|----------|
| 2026-06-08 | zakburak | Pinky target (look-ahead), Clyde flee radius, Inky symmetric target, ghost path debug view, ghost size scaling |
| 2026-06-09 | zakburak | Ghost frightened / eaten state machine; collision detection overhaul; BFS reachable cells; pacgum collection with interpolation; game-over / respawn logic; score popups; hitbox tuning; boundary clamping; wall detection fix |
| 2026-06-09 | elsahin | Config validation + safe defaults + WASD support; game/pause scenes + input handling; bitmap font HUD (score, level, time) |

**Goal:** complete all game-play rules and ghost behaviours; wire up scenes and HUD.

---

### Phase 4 — Polish & Documentation (2026-06-10)

| Date | Author | Activity |
|------|--------|----------|
| 2026-06-10 | zakburak | Cheat menu (invincible, ghost freeze, speed boost, level skip, +1 life); ghost path/target debug overlays; ready-state display; death timer |
| 2026-06-10 | zakburak | Maze tile fallback debugger; bitmap font robustness |
| 2026-06-10 | zakburak | **Fruit system:** spawning at 30 %/70 % pacgum thresholds, 9-second duration, level-indexed point table (cherry → galaxian) |
| 2026-06-10 | zakburak | Config robustness: improved error messages, adjusted name-length limits |
| 2026-06-10 | elsahin | Rename `godmode` → `invincible`; font scaling fixes across all scenes |
| 2026-06-10 | elsahin | Win scene (score submission); game-over scene (score submission); maze surface regeneration on level change |
| 2026-06-10 | zakburak | Comprehensive README |

**Goal:** feature-complete, polished, and documented game ready for peer review.

---

### Phase 5 — Extended Features (2026-06-16 → 2026-06-17)

| Date | Author | Activity |
|------|--------|----------|
| 2026-06-16 | elsahin | **Mouse navigation:** click-based item selection in all menus and scenes |
| 2026-06-16 | elsahin | Config clamping improvements; recursion-limit increase for large maze generation |
| 2026-06-16 | elsahin | New `level_count` config key (default 5); scoreboard reordering fix |
| 2026-06-16 | zakburak | **Secret mode skin:** dedicated Pac-Man sprites (right/death animations) for "Fermis" mode |
| 2026-06-16 | zakburak | **Asset manifest system:** `assets/manifest.json` + `src/views/assets.py`; dynamic skin/animation loading with `OverlaySkin` fallback |
| 2026-06-16 | zakburak | **Secret mode activation:** cheat-code sequence `fermis` typed on main menu; `config.json` `"secret"` flag; title changes to FERMIS in pink |
| 2026-06-16 | elsahin | Maze dimensions and speed tuning in `config.json` |
| 2026-06-17 | zakburak | Fallback manifest in `settings.py` when `assets/manifest.json` is missing |
| 2026-06-17 | zakburak | Ghost fright duration decreases by 500 ms per level (`FRIGHTENED_REDUCTION_PER_LEVEL`) |
| 2026-06-17 | zakburak | Sprite rendering improvements; config fine-tuning |

**Goal:** extend replayability (more levels, skins, mouse UX) and improve difficulty scaling.

---

### Phase 6 — Packaging, Deployment & Hardening (2026-06-17)

| Date | Author | Activity |
|------|--------|----------|
| 2026-06-17 | zakburak | **PyInstaller packaging:** `pacman.spec` (standalone build, embedded assets + config); dynamic config-path resolution and resource handling via `src/paths.py` (`sys._MEIPASS`) |
| 2026-06-17 | zakburak | **Deployment:** game published on Itch.io; `make build` / `make package` targets (zip ready to upload); README link added |
| 2026-06-17 | zakburak | **Manifest hardening:** geometry validation (`_validate_block`), RGB safeguards (`_checked_rgb`, components bounded to 0–255), integer-cast safety in drawing functions |
| 2026-06-17 | zakburak | Config hardening: `lives` clamped to `[1, 99]`; ghost speed capped at `GHOST_SPEED_MAX = 10.0` regardless of config |

**Goal:** make the project shippable (standalone build + online release) and crash-proof against hostile config and manifest files during peer review.

---

## 3. Planned vs Actual Progress

| Milestone | Planned | Actual | Delta |
|-----------|---------|--------|-------|
| Prototype / tile rendering | Week 1 (May 25–30) | May 25–30 | On time |
| Core engine + MVC | Week 2 (Jun 1–6) | Jun 3–7 | +1 day |
| Ghost AI (all 4 behaviours) | Week 2 | Jun 8 | +2 days |
| Game mechanics (lives, timer, score) | Week 2 | Jun 9 | +3 days |
| UI scenes + HUD | Week 2 | Jun 9–10 | +4 days |
| Cheat mode | Week 3 | Jun 10 | On schedule |
| Fruit system | Week 3 | Jun 10 | On schedule |
| README + documentation | Week 3 | Jun 10 | On time |
| Mouse navigation | — | Jun 16 | Added post-release |
| Asset manifest + skin system | — | Jun 16 | Added post-release |
| Secret mode ("Fermis") | — | Jun 16 | Added post-release |
| Ghost fright scaling per level | — | Jun 17 | Added post-release |
| Deployment (Itch.io) | Week 3 | Jun 17 | **Done** (PyInstaller + Itch.io) |
| Manifest geometry/RGB hardening | — | Jun 17 | Added post-release |
| Config ranges (`lives`, ghost-speed cap) | — | Jun 17 | Added post-release |
| Project management documents | Week 3 | Jun 10 | Late |

---

## 4. Project Analysis & Technical Choices

| Decision | Alternative considered | Reason chosen |
|----------|----------------------|---------------|
| Doubled grid (each maze cell → 2×2 pixels) | Direct pixel mapping | Makes wall collision straightforward: a wall cell is exactly one tile; no sub-cell arithmetic |
| BFS pathfinding for ghosts | Euclidean distance heuristic | Guarantees optimal path in the corridor graph; simple to implement; fast enough at 60 FPS for 4 ghosts |
| JSON with `#`/`//` comment stripping | TOML / YAML | Subject specifies JSON + comment support; no extra dependency |
| `uv` as package manager | `pip` / `venv` | Faster installs, lockfile, reproducible environments |
| Scene system (no direct scene references) | Global game state | Keeps scenes decoupled; `change_scene()` is the only coupling point |
| Persistent highscores in JSON list-of-objects | SQLite / CSV | Human-readable, no dependency, trivial to edit for testing |

---

## 5. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| External `mazegenerator` package interface changes | Low | High | Locked in `uv.lock`; peer reviewer re-installs the same wheel from `lib/` |
| Ghost BFS too slow on large mazes | Medium | Medium | Empirically tested up to 30×30; BFS on the passage graph (not pixel grid) is O(n) cells |
| Timer drift after long pauses | Medium | Low | `_tick_timer` clamps dt to 100 ms per frame |
| Config file modified to invalid values during defence | High | Low | All keys clamped to safe defaults; no traceback possible |
| Manifest file corrupted/edited during defence | Medium | Medium | Full structural + geometry/RGB validation; baked-in fallback manifest; tested against 26 corruption cases — always falls back, never crashes |
| Deployment not ready for peer review | ~~High~~ | ~~High~~ | **Resolved** — standalone PyInstaller build (`make package`) + published on Itch.io |

---

## 6. Acceptance Test Plan

### 6.1 Mandatory features

| Feature | Test | Status |
|---------|------|--------|
| Launch with `python3 pac-man.py config.json` | Run from CLI | ✅ |
| Invalid config → no traceback, clear message | Pass a broken JSON | ✅ |
| Unknown config key → silently ignored | Add `"foo": 1` | ✅ |
| Maze generated by external package | Check `from mazegenerator import MazeGenerator` | ✅ |
| Level 1 uses fixed seed | Run twice, same maze | ✅ |
| Level 2+ uses random seed | Run twice, different maze | ✅ |
| Pacgums fill corridors | Visual inspection | ✅ |
| Super-pacgums in 4 corners | Visual inspection | ✅ |
| 4 ghosts, one per corner | Visual inspection | ✅ |
| Pac-Man starts in middle | Visual inspection | ✅ |
| Arrow keys + WASD movement | Keyboard test | ✅ |
| Ghost chase behaviour (Blinky/Pinky/Inky/Clyde) | Enable path debug overlay | ✅ |
| Frightened mode after super-pacgum | Eat super-pacgum | ✅ |
| Eating frightened ghost → score + return | Eat ghost | ✅ |
| Losing a life on ghost contact | Walk into ghost | ✅ |
| Respawn in middle after death | Lose a life | ✅ |
| Game over when 0 lives | Lose 3 lives | ✅ |
| Level clear when all pacgums eaten | Eat all dots | ✅ |
| Score and lives carry over between levels | Complete a level | ✅ |
| Level timer visible, ends level | Wait 90 s | ✅ |
| Pause / resume (P or Escape) | Press P | ✅ |
| Main menu → Start / Highscores / Instructions / Exit | Navigate menus | ✅ |
| Highscore entry (win or lose) | Finish a game | ✅ |
| Highscore persisted to `scoreboard.json` | Check file after game | ✅ |
| Top 10 displayed in menu | View highscores | ✅ |

### 6.2 Cheat mode

| Feature | Test | Status |
|---------|------|--------|
| Open cheat menu with `C` | Press C in-game | ✅ |
| Invincible toggle | Enable, walk into ghost | ✅ |
| Ghost freeze toggle | Enable, ghosts stop | ✅ |
| Speed boost toggle | Enable, Pac-Man faster | ✅ |
| +1 life | Press in cheat menu | ✅ |
| Skip level | Press in cheat menu | ✅ |
| Show ghost paths debug | Toggle in cheat menu | ✅ |
| Show ghost targets debug | Toggle in cheat menu | ✅ |

### 6.3 Extended features (Phase 5)

| Feature | Test | Status |
|---------|------|--------|
| Fruit appears at 30 % pacgums eaten | Eat ~1/3 of dots | ✅ |
| Fruit appears again at 70 % pacgums eaten | Eat ~2/3 of dots | ✅ |
| Fruit disappears after 9 s | Wait without collecting | ✅ |
| Fruit points scale with level | Check score on levels 1–5 | ✅ |
| Mouse click selects menu item | Click option in main menu | ✅ |
| `level_count` in config limits level total | Set `"level_count": 2`, win level 2 | ✅ |
| `"secret": true` in config enables Fermis skin | Edit config, launch game | ✅ |
| Typing `fermis` on menu activates secret mode | Spell out the code in menu | ✅ |
| Secret mode changes title to FERMIS (pink) | Visual inspection | ✅ |
| Fright duration shorter on higher levels | Compare level 1 vs level 5 after super-pacgum | ✅ |
| Fallback manifest when `assets/manifest.json` missing | Remove manifest, launch | ✅ |

### 6.4 Known bugs found & fixed

| Bug | Commit fix |
|-----|-----------|
| Pac-Man could exit maze boundary | `9d9166b` — boundary clamping added |
| Wall detection returned false for out-of-bounds | `215e75b` — fix OOB → returns `True` (wall) |
| Ghost eaten timer not expiring correctly | `1502f18` — state machine rework |
| Speed variable name typo (Pac-Man) | `7f47f7f` — variable rename |
| `godmode` config key inconsistency | `0c02655` — renamed to `invincible` |

### 6.5 Packaging & robustness (Phase 6)

| Feature | Test | Status |
|---------|------|--------|
| Standalone build | `make build` → run `dist/pacman/pacman` with no system Python | ✅ |
| Package for release | `make package` → `dist/pacman-linux.zip` + editable config next to exe | ✅ |
| Frozen build finds assets | Launch packaged exe (resources via `sys._MEIPASS`) | ✅ |
| Highscores writable in frozen build | Finish a game from the packaged exe, score persists | ✅ |
| Online availability | Download from Itch.io and play | ✅ |
| Corrupted manifest → fallback | 26 corruption cases (bad JSON, missing keys, out-of-range RGB, bad geometry, broken skin) | ✅ — always falls back, no traceback |
| Missing manifest → fallback | Remove `assets/manifest.json`, launch | ✅ |
| `lives` out of range | Set `"lives": 9999` → clamped to 99 | ✅ |
| Excessive `ghost_speed` | Set huge speed → capped at 10.0 | ✅ |

---

## 7. Blocking Points & Conflicts

| Point | Description | Resolution |
|-------|-------------|------------|
| Maze generator interface | The assigned `mazegenerator` package encodes walls as 4-bit per cell; required careful mapping to the doubled grid | Documented in `src/models/maze.py`; `perfect=False` mandatory |
| Ghost speed vs. BFS path length (eaten mode) | Ghost needed to arrive at spawn exactly when timer expired | Dynamic speed = BFS path length / remaining time (in seconds) |
| Inter-frame pacgum collection | At high speed, Pac-Man could skip over a pacgum cell between frames | `cells_visited` stores previous + current position; all intermediate cells checked |
| Bitmap font missing glyphs | Fallback maze tile rendering exposed missing font asset path | `b769e38` — fallback debugger + error-resistant font loading |
| Manifest missing at launch | If `assets/manifest.json` absent, asset loading failed silently | `1faca82` — full fallback manifest baked into `settings.py` |
| Manifest with hostile values | Out-of-range RGB / bad block geometry could crash pygame at surface creation | `b7da3b1` — geometry validation + RGB safeguards (0–255), bad values → fallback |
| Maze generation crash on large grids | Python recursion limit too low for big mazes | `0145b34` — explicit `sys.setrecursionlimit` increase |
| Frozen build couldn't find assets / write scores | PyInstaller bundle is read-only and relocates resources | `ea53f36` — `src/paths.py` resolves `sys._MEIPASS` + per-platform user-data dir |
