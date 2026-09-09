# camera.py — smooth sledování hráče s dead zone a clampem na hranice mapy

import pygame
from src.core.settings import SCREEN_W, SCREEN_H


class Camera:
    def __init__(self, map_pixel_w: int, map_pixel_h: int):
        self.map_w = map_pixel_w
        self.map_h = map_pixel_h
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Dead zone — kamera se nehýbe pokud je hráč v tomto středovém pásu
        self.dead_x = SCREEN_W * 0.25
        self.dead_y = SCREEN_H * 0.30

        # Smoothing — kolik % chyby opravíme za snímek (1.0 = okamžitě)
        self.smooth = 0.12

    def update(self, target_rect: pygame.Rect):
        """target_rect = rect hráče ve světových souřadnicích."""
        # Cílová pozice kamery: hráč ve středu
        target_x = target_rect.centerx - SCREEN_W // 2
        target_y = target_rect.centery - SCREEN_H // 2

        # Lerp (lineární interpolace pro plynulý pohyb)
        self.offset_x += (target_x - self.offset_x) * self.smooth
        self.offset_y += (target_y - self.offset_y) * self.smooth

        # Clamp — nepřekrůčíme hranice mapy
        self.offset_x = max(0, min(self.offset_x, self.map_w - SCREEN_W))
        self.offset_y = max(0, min(self.offset_y, self.map_h - SCREEN_H))

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        return int(wx - self.offset_x), int(wy - self.offset_y)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Vrátí rect posunutý o offset kamery (pro vykreslení na obrazovku)."""
        return rect.move(-int(self.offset_x), -int(self.offset_y))
