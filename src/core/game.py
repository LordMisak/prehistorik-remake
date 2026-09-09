# game.py — main loop a scene manager

import pygame
import sys
from src.core.settings import SCREEN_W, SCREEN_H, TITLE, FPS


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()
        self.running = True

        # Scene manager: slovník jméno -> třída scény (lazy import)
        self._scenes: dict = {}
        self._current: "Scene | None" = None

    def register(self, name: str, scene_cls):
        """Zaregistruje scénu pod daným jménem."""
        self._scenes[name] = scene_cls

    def switch(self, name: str, **kwargs):
        """Přepne na scénu — vytvoří novou instanci s referencí na Game."""
        if self._current and hasattr(self._current, "on_exit"):
            self._current.on_exit()
        self._current = self._scenes[name](self, **kwargs)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                    self.running = False  # alt+F4 fallback

            if self._current:
                self._current.handle_events(events)
                self._current.update(dt)
                self._current.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()


class Scene:
    """Základní třída pro všechny scény — přepis metod dle potřeby."""
    def __init__(self, game: Game):
        self.game = game

    def handle_events(self, events: list):
        pass

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        pass

    def on_exit(self):
        pass
