"""Scène de jeu : enveloppe le modèle Game et sa vue."""

from .scene import Scene
from ..models.game import Game
from ..views.game_view import GameView
from ..controllers.input_controller import InputController


class GameScene(Scene):
    """Fait tourner une partie (modèle + vue + entrées clavier)."""

    def __init__(self, app):
        super().__init__(app)
        self.game = Game(app.config)
        self.view = GameView(app.screen, self.game.maze)
        self.input = InputController()

    def handle_events(self, events, now):
        action = self.input.apply(events, self.game)
        if action == "pause":
            from .pause_scene import PauseScene
            self.app.change_scene(PauseScene(self.app, self))
        elif action == "cheat":
            from .cheat_scene import CheatScene
            self.app.change_scene(CheatScene(self.app, self))

    def update(self, now):
        self.game.update(now)
        if self.game.game_over:
            from .game_over_scene import GameOverScene
            self.app.change_scene(GameOverScene(self.app, self.game.score))
        elif self.game.won:
            from .win_scene import WinScene
            self.app.change_scene(WinScene(self.app, self.game.score))

    def draw(self, screen, now):
        self.view.render(self.game, now)
