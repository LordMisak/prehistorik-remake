# gameplay.py — hlavní herní scéna: mapa, hráč, kamera, HUD, parallax

import pygame
from src.core.game import Scene
from src.core.settings import *
from src.world.tilemap import TileMap, TILE_SOLID, TILE_GRASS, TILE_EMPTY, TILE_ONEWAY
from src.systems.camera import Camera
from src.systems.hud import HUD
from src.entities.player import Player


# ---------------------------------------------------------------------------
# TESTOVACÍ LEVEL 1 — inline mapa (nahradíme Tiled JSON)
# 0=vzduch, 1=solid, 2=tráva, 4=one-way platforma
# ---------------------------------------------------------------------------
def build_test_map():
    E = TILE_EMPTY
    S = TILE_SOLID
    G = TILE_GRASS
    O = TILE_ONEWAY

    rows = [
        # 0         1         2         3         4         5
        # 0123456789012345678901234567890123456789012345678901234567
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",  # row 0  strop
        "S...........................................................S",  # 1
        "S...........................................................S",  # 2
        "S...........................................................S",  # 3
        "S...........................................................S",  # 4
        "S...........................................................S",  # 5
        "S...........................................................S",  # 6
        "S...........GG......................................GGG.....S",  # 7
        "S.........OOOO.....GGG.......................OOOOOOOO.......S",  # 8
        "S..................................................................S",  # 9
        "S......GG...........GG.....GGG.............................GG.....S",  # 10
        "S....OOOO.......OOOOOO.OOOOOOO...........................OOOO.....S",  # 11
        "S...........................................................S",  # 12
        "S...........................................................S",  # 13
        "GGGGGGGGGGGGGGGGGGGGGGGGGG..GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # 14 zem s propastí
        "SSSSSSSSSSSSSSSSSSSSSSSSSS..SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",  # 15
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",  # 16 dno
    ]

    mapping = {"S": TILE_SOLID, "G": TILE_GRASS, "O": TILE_ONEWAY, ".": TILE_EMPTY}
    data = []
    for r in rows:
        data.append([mapping.get(c, TILE_EMPTY) for c in r])
    # Zarovnat délky řádků
    max_cols = max(len(r) for r in data)
    for r in data:
        while len(r) < max_cols:
            r.append(TILE_SOLID)
    return data


class ParallaxLayer:
    """Jednoduchá parallax vrstva — opakující se obdélník."""
    def __init__(self, color, speed: float, y: int, h: int, detail=None):
        self.color = color
        self.speed = speed   # 0 = fixní, 1 = stejně rychlá jako mapa
        self.y = y
        self.h = h
        self.detail = detail  # seznam extra shapes [(color, rect_rel), ...]

    def draw(self, screen: pygame.Surface, camera_x: float):
        ox = int(camera_x * self.speed) % SCREEN_W
        pygame.draw.rect(screen, self.color, (0, self.y, SCREEN_W, self.h))
        if self.detail:
            for (dc, dw, dh, dy_off) in self.detail:
                x = (-ox) % (dw + 60)
                while x < SCREEN_W:
                    pygame.draw.rect(screen, dc, (x, self.y + dy_off, dw, dh), border_radius=4)
                    x += dw + 60


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        # Mapa
        map_data = build_test_map()
        self.tilemap = TileMap(map_data)

        # Hráč (spawnuje ve světových souřadnicích)
        self.player = Player(2 * TILE_SIZE, 12 * TILE_SIZE)

        # Kamera
        self.camera = Camera(self.tilemap.pixel_w, self.tilemap.pixel_h)

        # HUD
        self.hud = HUD()

        # Parallax vrstvy (vzadu → vepředu)
        self.parallax = [
            ParallaxLayer((135, 180, 220), 0.0,  0,   SCREEN_H),           # obloha
            ParallaxLayer((170, 200, 170), 0.05, 300, 200,                 # vzdálené kopce
                detail=[((150, 180, 150), 80, 120, 10)]),
            ParallaxLayer((110, 150, 100), 0.15, 380, 180,                 # blízké kopce
                detail=[((90, 130, 80), 60, 90, 5)]),
            ParallaxLayer((70, 110, 60),  0.3,  430, 140),                 # stromy (silueta)
        ]

        # Pauza
        self.paused = False
        self.font_pause = pygame.font.Font(None, 80)

        # Respawn timer
        self.respawn_timer = 0

    # ------------------------------------------------------------------

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                if e.key == pygame.K_F1 and self.paused:
                    self.game.switch("menu")

    def update(self, dt):
        if self.paused:
            return

        keys = pygame.key.get_pressed()

        # Pokud je hráč mrtvý — čekat a respawnovat
        if self.player.is_dead:
            self.respawn_timer += 1
            if self.respawn_timer > 90:
                self.respawn_timer = 0
                if self.player.lives > 0:
                    self._respawn()
                else:
                    self.game.switch("menu")
            return

        self.player.handle_input(keys)
        self.player.update(self.tilemap)
        self.camera.update(self.player.rect)

    def _respawn(self):
        self.player.rect.topleft = (2 * TILE_SIZE, 12 * TILE_SIZE)
        self.player.vx = 0
        self.player.vy = 0
        self.player.hearts = self.player.max_hearts
        self.player.bones  = self.player.max_bones
        from src.entities.player import State
        self.player.state = State.IDLE

    def draw(self, screen: pygame.Surface):
        # 1. Parallax pozadí
        for layer in self.parallax:
            layer.draw(screen, self.camera.offset_x)

        # 2. Tile mapa
        self.tilemap.draw(screen, self.camera)

        # 3. Hráč
        self.player.draw(screen, self.camera)

        # 4. HUD
        self.hud.draw(screen, self.player)

        # 5. Pauza overlay
        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            ps = self.font_pause.render("PAUZA", True, C_WHITE)
            screen.blit(ps, (SCREEN_W//2 - ps.get_width()//2, SCREEN_H//2 - 60))
            hint = pygame.font.Font(None, 30).render("ESC = pokračovat    F1 = menu", True, (200, 200, 200))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H//2 + 20))

        # 6. Smrt overlay
        if self.player.is_dead:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((80, 0, 0, int(min(self.respawn_timer * 2, 160))))
            screen.blit(overlay, (0, 0))
            if self.respawn_timer > 30:
                ds = self.font_pause.render("ZEMŘEL JSI!", True, C_RED)
                screen.blit(ds, (SCREEN_W//2 - ds.get_width()//2, SCREEN_H//2 - 40))
