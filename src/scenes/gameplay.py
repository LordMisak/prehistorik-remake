# gameplay.py — hlavní herní scéna

import pygame
from src.core.game import Scene
from src.core.settings import *
from src.world.tilemap import TileMap, TILE_SOLID, TILE_GRASS, TILE_EMPTY, TILE_ONEWAY
from src.systems.camera import Camera
from src.systems.renderer import Background, PlayerRenderer, HUDRenderer
from src.entities.player import Player, State


def build_test_map():
    S = TILE_SOLID
    G = TILE_GRASS
    O = TILE_ONEWAY
    E = TILE_EMPTY

    # 60 sloupců, 20 řádků — číslice = typ tile
    raw = [
        "............................................................",  # row 0 vzduch (byl strop)
        "............................................................",
        "............................................................",
        "............................................................",
        "............................................................",
        ".......................GGG...................................",
        "...................OOOOOOO..................................",
        "............GGG...........GGG...............................",
        "........OOOOOOO.......OOOOOOO...............................",
        "............................................................",
        "............................................................",
        "....GGG...........GGG.....GGG...............................",
        ".OOOOOOO.......OOOOOOO.OOOOOOO............................O.",
        "............................................................",
        "............................................................",
        "GGGGGGGGGGGGGGGGGGGGGGGGGG..GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSS..SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS.",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
    ]
    mapping = {"S": TILE_SOLID, "G": TILE_GRASS, "O": TILE_ONEWAY, ".": TILE_EMPTY}
    data = []
    for r in raw:
        data.append([mapping.get(c, TILE_EMPTY) for c in r])
    max_cols = max(len(r) for r in data)
    for r in data:
        while len(r) < max_cols:
            r.append(TILE_SOLID)
    return data


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        map_data = build_test_map()
        self.tilemap = TileMap(map_data)
        self.player  = Player(2 * TILE_SIZE, 13 * TILE_SIZE)
        self.camera  = Camera(self.tilemap.pixel_w, self.tilemap.pixel_h)

        self.bg      = Background(SCREEN_W, SCREEN_H)
        self.p_rend  = PlayerRenderer()
        self.hud     = HUDRenderer(SCREEN_W, SCREEN_H)

        self.paused = False
        self.font_pause = pygame.font.Font(None, 80)
        self.respawn_timer = 0

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
        if self.player.is_dead:
            self.respawn_timer += 1
            if self.respawn_timer > 90:
                self.respawn_timer = 0
                if self.player.lives > 0:
                    self._respawn()
                else:
                    self.game.switch("menu")
            return
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(self.tilemap)
        self.camera.update(self.player.rect)

    def _respawn(self):
        self.player.rect.topleft = (2 * TILE_SIZE, 13 * TILE_SIZE)
        self.player.vx = 0
        self.player.vy = 0
        self.player.hearts = self.player.max_hearts
        self.player.bones  = self.player.max_bones
        self.player.state  = State.IDLE

    def draw(self, screen: pygame.Surface):
        # 1. Parallax pozadí
        self.bg.draw(screen, self.camera.offset_x)

        # 2. Tile mapa
        self.tilemap.draw(screen, self.camera)

        # 3. Hráč
        self.p_rend.draw(screen, self.player, self.camera)

        # 4. HUD dole
        self.hud.draw(screen, self.player)

        # 5. Pauza
        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            ps = self.font_pause.render("PAUZA", True, (255, 255, 255))
            screen.blit(ps, (SCREEN_W//2 - ps.get_width()//2, SCREEN_H//2 - 60))
            hint = pygame.font.Font(None, 30).render("ESC = pokračovat    F1 = menu", True, (200,200,200))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H//2 + 20))

        # 6. Smrt overlay
        if self.player.is_dead:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((80, 0, 0, min(self.respawn_timer * 2, 160)))
            screen.blit(overlay, (0, 0))
            if self.respawn_timer > 30:
                ds = self.font_pause.render("ZEMŘEL JSI!", True, (220, 50, 50))
                screen.blit(ds, (SCREEN_W//2 - ds.get_width()//2, SCREEN_H//2 - 40))
