# tilemap.py — jednoduchá tile mapa z 2D pole + renderer

import pygame
from src.core.settings import TILE_SIZE, C_GROUND, C_GRASS, C_BLACK


# Typy dlaždic
TILE_EMPTY  = 0
TILE_SOLID  = 1   # pevná zem
TILE_GRASS  = 2   # tráva navrchu
TILE_SPIKE  = 3   # hroty = instant smrt
TILE_ONEWAY = 4   # průchozí zdola


# Barvy dlaždic (placeholder, nahradíme sprity)
TILE_COLORS = {
    TILE_SOLID:  (100, 70, 40),
    TILE_GRASS:  (60, 140, 50),
    TILE_SPIKE:  (180, 50, 50),
    TILE_ONEWAY: (120, 90, 55),
}

TILE_LETHAL = {TILE_SPIKE}
TILE_SOLID_SET = {TILE_SOLID, TILE_GRASS, TILE_ONEWAY}


class TileMap:
    def __init__(self, data: list[list[int]]):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if self.rows else 0
        self.pixel_w = self.cols * TILE_SIZE
        self.pixel_h = self.rows * TILE_SIZE

    def get(self, col: int, row: int) -> int:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.data[row][col]
        return TILE_SOLID  # mimo mapu = pevná zeď

    def is_solid(self, col: int, row: int) -> bool:
        return self.get(col, row) in TILE_SOLID_SET

    def is_lethal(self, col: int, row: int) -> bool:
        return self.get(col, row) in TILE_LETHAL

    def is_oneway(self, col: int, row: int) -> bool:
        return self.get(col, row) == TILE_ONEWAY

    def draw(self, screen: pygame.Surface, camera):
        """Kreslí pouze viditelné dlaždice (frustum culling)."""
        cx, cy = int(camera.offset_x), int(camera.offset_y)
        col_start = max(0, cx // TILE_SIZE)
        col_end   = min(self.cols, col_start + screen.get_width() // TILE_SIZE + 2)
        row_start = max(0, cy // TILE_SIZE)
        row_end   = min(self.rows, row_start + screen.get_height() // TILE_SIZE + 2)

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                t = self.data[row][col]
                if t == TILE_EMPTY:
                    continue
                color = TILE_COLORS.get(t, (200, 200, 200))
                rx = col * TILE_SIZE - cx
                ry = row * TILE_SIZE - cy
                rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)
                # outline pro lepší čitelnost
                pygame.draw.rect(screen, C_BLACK, rect, 1)

                # Tráva — zelený proužek navrchu
                if t == TILE_GRASS:
                    pygame.draw.rect(screen, (80, 180, 60), (rx, ry, TILE_SIZE, 6))
