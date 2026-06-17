*This project has been created as part of the 42 curriculum by zakburak, elsahin.*

# Pac-Man

## Description

A complete, playable Pac-Man game written in Python using Pygame. The game faithfully recreates the classic 1980 Namco arcade experience: Pac-Man navigating a maze, eating pacgums, avoiding ghosts, and collecting power pellets to turn the tables. It features procedurally generated mazes (via an external maze generator package), a persistent highscore system, a cheat menu for evaluation, and a polished fullscreen UI with menu, game, pause, win, and game-over screens.

The project is structured around an MVC pattern (models / views / controllers / scenes) and follows the flake8 + mypy coding standard required by the subject.

## Instructions

### Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### Installation

```bash
make install
```

This runs `uv sync`, which creates a virtual environment and installs all dependencies (Pygame, the local mazegenerator wheel).

### Running the game

```bash
make run
# or directly:
uv run python pac-man.py config.json
```

The game takes **exactly one argument**: a JSON configuration file.

### Other Makefile targets

| Target | Description |
|--------|-------------|
| `make install` | Install dependencies via `uv sync` |
| `make run` | Launch the game with `config.json` |
| `make debug` | Launch the game under `pdb` |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `build/`, `dist/` |
| `make build` | Build a standalone executable into `dist/pacman/` (PyInstaller) |
| `make package` | Build + bundle an editable `config.json` + zip into `dist/pacman-linux.zip` |
| `make lint` | Run `flake8` + `mypy` (standard flags) |
| `make lint-strict` | Run `flake8` + `mypy --strict` |

### Controls

| Key / Input | Action |
|-------------|--------|
| Arrow keys / WASD | Move Pac-Man |
| P / Escape | Pause |
| C | Open cheat menu (during game or from pause) |
| Enter / Space | Confirm selection in menus |
| Escape | Back / close overlay |
| Mouse click | Navigate and select in menus |

---

## Configuration

The game reads a JSON configuration file passed as its only argument. Lines starting with `#` or `//` are treated as comments and ignored.

On missing or invalid keys the game logs a warning to stderr, falls back to the safe default, and continues — it never crashes or prints a Python traceback.

### Supported keys and defaults

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `highscore_filename` | string | `"scoreboard.json"` | Path to the highscore file |
| `width` | int > 0 | `20` | Maze width — clamped to `[5, 35]` |
| `height` | int > 0 | `20` | Maze height — clamped to `[5, 35]` |
| `lives` | int > 0 | `3` | Starting lives — clamped to `[1, 99]` |
| `pacgum` | int ≥ 0 | `42` | (reserved — placed automatically from maze) |
| `points_per_pacgum` | int ≥ 0 | `10` | Points for eating a pacgum |
| `points_per_super_pacgum` | int ≥ 0 | `50` | Points for eating a super-pacgum |
| `points_per_ghost` | int ≥ 0 | `200` | Points for eating a frightened ghost |
| `seed` | int ≥ 0 | `42` | Seed used for level 1 (subsequent levels use random seeds) |
| `level_max_time` | int > 0 | `90` | Time limit per level in seconds |
| `pacman_speed` | float > 0 | `1.0` | Base Pac-Man speed multiplier |
| `ghost_speed` | float > 0 | `1.0` | Base ghost speed multiplier (per-level speed is capped at `10.0`) |
| `invincible` | bool | `false` | Start with invincibility enabled |
| `level_count` | int > 0 | `5` | Number of levels to complete for a full win |
| `secret` | bool | `false` | Enable secret "Fermis" skin with alternate Pac-Man textures |

Out-of-range integers are **clamped** to the nearest bound (with a warning on stderr) instead of crashing; invalid types fall back to the default.

### Minimal example (`config.json`)

```json
{
    "width": 10,
    "height": 10,
    "pacman_speed": 0.8,
    "ghost_speed": 0.5,
    "points_per_ghost": 200,
    "lives": 3
}
```

---

## Highscore System

### How it works

Highscores are stored in a JSON file on disk (default: `scoreboard.json` next to the game). The file is loaded at startup and saved whenever a game ends (win or lose). The player is prompted to enter their name (max 10 characters, letters, digits, and spaces), which is normalised to uppercase.

The file format is a JSON array of objects:

```json
[
  {"name": "ALICE", "score": 4200},
  {"name": "BOB",   "score": 3100}
]
```

The system keeps up to 100 entries on disk and displays the top 10 in the highscore screen. A legacy dict format (`{"name": score}`) is also accepted in reading and silently migrated to the list format on the next save.

All file errors (missing file, invalid JSON, unexpected structure) are silently swallowed: the loader returns an empty list and the game continues normally.

### Why this implementation

The JSON list-of-objects format was chosen because it is human-readable, easily edited by hand for testing, and requires no external database dependency. The file is small (at most a few hundred bytes), so reading and rewriting it in full on each save is trivially fast and keeps the logic simple and robust.

---

## Maze Generation

The project uses an external `mazegenerator` package (provided as a `.whl` in `lib/`) without any modification. The package is imported via `from mazegenerator import MazeGenerator`.

### Integration (`src/models/maze.py`)

```python
generator = MazeGenerator(size=(cols, rows), seed=seed, perfect=False)
```

`perfect=False` is mandatory: it produces Pac-Man-compatible corridors with multiple paths instead of a perfect (tree-shaped) maze.

The generator returns a 2D grid where each cell encodes its walls as 4 bits (N=1, E=2, S=4, W=8). `Maze._build_wall_grid()` converts this into a **doubled grid** (each original cell becomes a 2×2 block plus shared wall cells), where `1` = wall and `0` = passage. This doubled representation makes pixel-level collision detection straightforward.

### Level seeding

- **Level 1**: the fixed seed from `config.json` (default 42) — always the same maze.
- **Levels 2+**: a fresh `random.randint(0, 2**31 - 1)` seed — a new maze every time.

### Pacgum placement

All reachable passage cells (found via BFS from the maze entry) become pacgums. The four cells closest to the four corners are promoted to super-pacgums (power pellets).

If the generator raises an exception (e.g., invalid size), the error propagates cleanly to `load_config` / `GameController`, which exits with a clear message.

---

## Implementation

### Game loop

The game runs at 60 FPS. Each frame the active `Scene` receives `handle_events → update → draw`. The `GameController` manages the current scene and the `change_scene` transition.

### Entities and movement

All entities (Pac-Man and ghosts) move in pixel space on the doubled grid. They snap to the centre of the nearest corridor tile at each intersection, which prevents wall clipping. Pac-Man stores the last two pixel positions per frame (`cells_visited`) so that pacgum collection and ghost collisions are checked on every grid cell crossed during fast movement, not just the final position.

### Ghost AI

Each ghost uses BFS on the passage grid to find the shortest path to its target:

| Ghost | Color | Target (normal mode) |
|-------|-------|----------------------|
| Blinky | Red | Pac-Man's current cell |
| Pinky | Pink | 1 cell ahead of Pac-Man |
| Inky | Cyan | Symmetric of Pac-Man w.r.t. Blinky |
| Clyde | Orange | Pac-Man if far (> 2 cells), else flees |

In **frightened** mode (after a super-pacgum is eaten) ghosts reverse direction once and then move randomly at intersections. In **eaten** mode ghosts rush back to their spawn using a dynamically adjusted speed (BFS path length / remaining time) so they arrive exactly when the eaten timer expires.

### Level progression

Ghosts gain +10 % speed per level (`GHOST_SPEEDUP_PER_LEVEL = 0.1`), capped at `GHOST_SPEED_MAX = 10.0` so an aggressive config can never make them uncatchable or unstable. The frightened duration after a super-pacgum is eaten decreases by 500 ms each level (`FRIGHTENED_REDUCTION_PER_LEVEL`), making later levels more dangerous. Score and lives carry over between levels. The number of levels is controlled by `level_count` (default 5). The level timer pauses naturally because `update()` is not called while the game is paused.

### Fruit system

Fruits appear at the centre of the maze twice per level, triggered at 30 % and 70 % of pacgums eaten. Each fruit stays visible for 9 seconds. The fruit type and point value advance with the level:

| Level | Fruit | Points |
|-------|-------|--------|
| 1 | Cherry | 100 |
| 2 | Strawberry | 300 |
| 3–4 | Orange | 500 |
| 5–6 | Apple | 700 |
| 7+ | Galaxian | 2000 |

### Cheat mode

Accessed with `C` during the game. Available toggles: godmode (invincibility), ghost freeze, speed boost (×2.5), show ghost BFS paths, show ghost targets. Actions: +1 life, skip level.

### Secret mode

Typing `f e r m i s` sequentially on the main menu activates the secret "Fermis" skin. The menu title changes to **FERMIS** (in pink) and Pac-Man is rendered with dedicated alternate sprites. The mode can also be enabled directly in `config.json` with `"secret": true`.

---

## Packaging & Deployment

The game is published on **Itch.io** and can be rebuilt as a standalone executable with PyInstaller — no Python installation is required to play the packaged build.

```bash
make build      # → dist/pacman/        (standalone, assets + config embedded)
make package    # build + editable config.json alongside the exe + dist/pacman-linux.zip
```

`pacman.spec` embeds the `assets/` folder and `config.json` into the bundle. `src/paths.py` resolves resource paths transparently whether the game runs from source or from a frozen build (via `sys._MEIPASS`). Because the bundled `config.json` is read-only, `make package` also drops an **editable** `config.json` next to the executable, so players can tweak settings without recompiling. Highscores are written to a per-platform user-data directory, which stays writable even when the bundle itself is read-only.

**Play online:** <https://thorfinn61.itch.io/pac-man>

---

## General Software Architecture

```
pac-man.py              Entry point — calls src/main.py:main()
src/
├── config.py           JSON loading, comment stripping, validation/clamping
├── highscores.py       Load/save highscore file (robust to all file errors)
├── paths.py            Resource/user-data path resolution (source vs frozen build)
├── main.py             main() — parse args, load config, start GameController
│
├── controllers/
│   ├── game_controller.py   Pygame init, main loop, scene switching
│   └── input_controller.py  Raw key → buffered direction for Pac-Man
│
├── models/
│   ├── game.py         Root game state: maze, entities, score, lives, timer
│   ├── maze.py         Maze model (doubled grid, pacgum sets, BFS reachability)
│   ├── pacman.py       Pac-Man entity (movement, collision, death/respawn)
│   └── ghost.py        Ghost base class + BFS AI + Blinky/Pinky/Inky/Clyde
│
├── scenes/
│   ├── scene.py        Abstract base scene
│   ├── menu_scene.py   Main menu (start, highscores, instructions, quit)
│   ├── game_scene.py   In-game HUD + game logic bridge
│   ├── pause_scene.py  Pause overlay (resume, cheat, main menu)
│   ├── cheat_scene.py  Cheat menu overlay
│   ├── game_over_scene.py   Game-over screen + name entry
│   ├── win_scene.py    Victory screen + name entry
│   ├── highscore_scene.py   Top-10 display
│   └── instructions_scene.py  Controls and rules
│
└── views/
    ├── game_view.py    Top-level renderer (maze + entities + HUD + fruits)
    ├── maze_view.py    Tile-based maze renderer (auto-tiling)
    ├── sprite_view.py  Animated sprite renderer for entities
    ├── sprites.py      SpriteSheet loader and frame extractor
    ├── assets.py       Asset manager: reads manifest.json, builds skin + animators
    ├── bitmap_font.py  Bitmap font renderer (from sprite sheet)
    └── settings.py     Manifest loading + validation + baked-in fallback; view constants
```

**Key relationships:**

- `GameController` owns the current `Scene` and the shared `SpriteSheet`.
- `GameScene` owns a `Game` instance (model root) and a `GameView` (renderer).
- `Game` owns `Maze`, `Pacman`, and the four `Ghost` instances.
- Scenes communicate only through `app.change_scene(next_scene)` — no direct scene-to-scene references except for the cheat menu, which holds a back-reference to `GameScene` to be able to resume it.

---

## Project Management

### Team organization

Full project management documents (timeline, risk analysis, acceptance tests, blocking points) are available in [project_management/](project_management/).

The project was developed by two contributors:

**zakburak** — core engine, game mechanics, and polish
- Project scaffolding: MVC structure, configuration loading, asset pipeline
- Maze model: doubled-grid representation, BFS reachability, pacgum/super-pacgum placement, auto-tiling renderer
- Pac-Man entity: movement, wall collision, boundary clamping, hitbox, animation state tracking
- Ghost AI: BFS pathfinding, individual targeting logic for Blinky, Pinky, Inky, and Clyde, frightened / eaten state machine, dynamic eaten-speed calculation, fright duration scaling per level
- Game loop: pacgum collection with inter-frame interpolation, ghost collision detection, score popups, level timer, respawn mechanics
- Fruit system: spawn triggers, duration timer, level-indexed point table
- Asset manifest: `assets/manifest.json` + `src/views/assets.py` skin system with default and secret overlay skins
- Secret mode: "Fermis" skin, cheat-code activation in menu, `config.json` flag
- Ready-state display and death condition based on elapsed time

**elsahin** — UI, scenes, and robustness
- Config validation: defaults, clamping on invalid values, recursion-limit fix for large mazes, WASD support
- New config keys: `level_count`, config value clamping
- Scene system: pause scene, game-over scene (score submission), win scene (score submission), highscore display
- Cheat menu: godmode, ghost freeze, speed boost, level skip, debug overlays (ghost paths and targets)
- Mouse interaction: click-based navigation in menus and scenes
- In-game HUD: bitmap font rendering, score / level / remaining time display
- Maze view refactor: surface regeneration on level change
- Font scaling and positioning across all scenes

### Contribution summary

| Contributor | Commits | Main areas |
|-------------|---------|------------|
| zakburak | ~60 | Engine, AI, gameplay, fruits, asset manifest, secret mode, packaging |
| elsahin | ~21 | UI, scenes, mouse nav, config robustness |

---

## Resources

### References

- [Pac-Man Wikipedia](https://en.wikipedia.org/wiki/Pac-Man) — history and original game rules
- [The Pac-Man Dossier (Jamey Pittman)](https://www.gamedeveloper.com/design/the-pac-man-dossier) — exhaustive reference on ghost AI and game mechanics
- [Pygame documentation](https://www.pygame.org/docs/) — display, events, drawing
- [mazegenerator package](https://pypi.org/project/mazegenerator/) — the A-Maze-ing package used for maze generation
- [mypy documentation](https://mypy.readthedocs.io/) — static type checking
- [flake8 documentation](https://flake8.pycqa.org/) — coding standard enforcement

### AI usage

AI (Claude) was used during this project for the following tasks:

- **Generating docstrings and type hints** for functions and classes, which was reviewed and adjusted before being committed.
- **Debugging movement and collision edge cases** — describing symptoms to the AI and comparing its suggestions against the actual game behaviour.
- **Drafting this README** — the structure and wording were generated with AI assistance, then reviewed and corrected to accurately reflect the actual implementation.
- **Explaining library interfaces** — in particular the `mazegenerator` bit-encoding and Pygame rect/surface APIs.

All AI-generated content was reviewed, tested, and validated before inclusion. The core game logic (ghost BFS, doubled-grid collision, timer clamping) was written and debugged manually.

### Link Itch.io
https://thorfinn61.itch.io/pac-man