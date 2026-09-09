# menu.py — hlavní menu s animovaným titulkem a parallax pozadím

import pygame
import math
from src.core.game import Scene
from src.core.settings import *


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.font_title  = pygame.font.Font(None, 120)
        self.font_sub    = pygame.font.Font(None, 40)
        self.font_hint   = pygame.font.Font(None, 28)
        self.tick = 0

        # Parallax cloudy vrstvy (placeholder obdélníky)
        self.clouds = [
            {"x": x * 180, "y": 80 + i * 30, "w": 120 + i * 20, "h": 40, "speed": 0.3 + i * 0.15}
            for i, x in enumerate(range(6))
            for _ in range(1)
        ]

        # Hory v pozadí
        self.mountains = [
            (100, 380, 200), (280, 350, 160), (450, 390, 180),
            (600, 360, 220), (760, 380, 170), (950, 355, 200),
            (1100, 370, 180),
        ]

        # Menu položky
        self.items = ["HRÁT", "NASTAVENÍ", "KONEC"]
        self.selected = 0
        self.blink = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.items)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.items)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm()

    def _confirm(self):
        if self.selected == 0:
            self.game.switch("gameplay")
        elif self.selected == 2:
            self.game.running = False

    def update(self, dt):
        self.tick += 1
        self.blink = (self.blink + 1) % 60
        for c in self.clouds:
            c["x"] = (c["x"] + c["speed"]) % (SCREEN_W + 200)

    def draw(self, screen):
        # Obloha — gradient (pygame nemá built-in, uděláme proužky)
        for y in range(SCREEN_H):
            ratio = y / SCREEN_H
            r = int(135 + (170 - 135) * ratio)
            g = int(180 + (210 - 180) * ratio)
            b = int(220 + (180 - 220) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_W, y))

        # Hory
        for (mx, my, mw) in self.mountains:
            pts = [(mx - mw//2, SCREEN_H), (mx, my), (mx + mw//2, SCREEN_H)]
            pygame.draw.polygon(screen, (90, 110, 100), pts)
            pygame.draw.polygon(screen, (130, 155, 140), pts, 2)

        # Mraky
        for c in self.clouds:
            pygame.draw.ellipse(screen, (240, 245, 255),
                (c["x"] - 140, c["y"], c["w"] + 80, c["h"]))
            pygame.draw.ellipse(screen, (255, 255, 255),
                (c["x"] - 120, c["y"] - 15, c["w"], c["h"] + 10))

        # Tráva / země
        pygame.draw.rect(screen, (60, 140, 50), (0, SCREEN_H - 80, SCREEN_W, 80))
        pygame.draw.rect(screen, (80, 160, 60), (0, SCREEN_H - 80, SCREEN_W, 10))

        # Titul — bounce animace
        bounce = math.sin(self.tick * 0.05) * 8
        title_surf = self.font_title.render("PREHISTORIK", True, C_BLACK)
        title_out  = self.font_title.render("PREHISTORIK", True, (230, 160, 40))
        x = SCREEN_W // 2 - title_surf.get_width() // 2
        y = int(160 + bounce)
        # outline efekt
        for ox, oy in [(-3,0),(3,0),(0,-3),(0,3)]:
            screen.blit(title_out, (x + ox, y + oy))
        screen.blit(title_surf, (x, y))

        sub = self.font_sub.render("REMAKE  2025", True, (80, 50, 20))
        screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, y + 90))

        # Menu položky
        for i, item in enumerate(self.items):
            col = C_WHITE if i == self.selected else (180, 160, 130)
            prefix = "> " if i == self.selected else "  "
            if i == self.selected and self.blink < 40:
                col = (255, 230, 80)
            surf = self.font_sub.render(prefix + item, True, col)
            screen.blit(surf, (SCREEN_W//2 - surf.get_width()//2, 380 + i * 55))

        # Hint
        hint = self.font_hint.render("SIPKY = výběr   ENTER/SPACE = potvrdit", True, (150, 130, 100))
        screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 40))
