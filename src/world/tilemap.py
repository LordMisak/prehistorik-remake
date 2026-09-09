# tilemap.py — tile mapa + rendering přes renderer.py

import pygame
from src.core.settings import TILE_SIZE

TILE_EMPTY  = 0
TILE_SOLID  = 1
TILE_GRASS  = 2
TILE_SPIKE  = 3
TILE_ONEWAY = 4

TILE_LETHAL    = {TILE_SPIKE}
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
        return TILE_SOLID

    def is_solid(self, col: int, row: int) -> bool:
        return self.get(col, row) in TILE_SOLID_SET

    def is_lethal(self, col: int, row: int) -> bool:
        return self.get(col, row) in TILE_LETHAL

    def is_oneway(self, col: int, row: int) -> bool:
        return self.get(col, row) == TILE_ONEWAY

    def draw(self, screen: pygame.Surface, camera):
        from src.systems.renderer import draw_stone_tile, draw_grass_tile, draw_oneway_tile
        ts = TILE_SIZE
        cx, cy = int(camera.offset_x), int(camera.offset_y)
        col_start = max(0, cx // ts)
        col_end   = min(self.cols, col_start + screen.get_width() // ts + 2)
        row_start = max(0, cy // ts)
        row_end   = min(self.rows, row_start + screen.get_height() // ts + 2)

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                t = self.data[row][col]
                if t == TILE_EMPTY:
                    continue
                rx = col * ts - cx
                ry = row * ts - cy
                if t == TILE_GRASS:
                    draw_grass_tile(screen, rx, ry, ts)
                elif t == TILE_ONEWAY:
                    draw_oneway_tile(screen, rx, ry, ts)
                elif t in (TILE_SOLID,):
                    draw_stone_tile(screen, rx, ry, ts)
                elif t == TILE_SPIKE:
                    # Hroty — červené trojúhelníky
                    for i in range(ts // 8):
                        bx = rx + i * 8
                        pts = [(bx, ry+ts), (bx+4, ry+ts-12), (bx+8, ry+ts)]
                        pygame.draw.polygon(screen, (180, 40, 40), pts)
