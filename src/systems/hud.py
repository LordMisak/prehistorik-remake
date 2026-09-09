# hud.py — vykreslení životy, srdce, kosti, skóre

import pygame
from src.core.settings import *


class HUD:
    def __init__(self):
        self.font_big  = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def draw(self, screen: pygame.Surface, player):
        # Poloprůhledný pruh nahoře
        bar = pygame.Surface((SCREEN_W, 48), pygame.SRCALPHA)
        bar.fill((20, 15, 10, 160))
        screen.blit(bar, (0, 0))

        # Životy (lebky/hlavy)
        for i in range(player.lives):
            pygame.draw.circle(screen, (220, 80, 80), (20 + i * 30, 24), 11)
            pygame.draw.circle(screen, C_BLACK, (20 + i * 30, 24), 11, 2)
            # křížek
            pygame.draw.line(screen, C_WHITE, (14+i*30, 18), (26+i*30, 30), 2)
            pygame.draw.line(screen, C_WHITE, (26+i*30, 18), (14+i*30, 30), 2)

        # Srdce
        sx = 120
        for i in range(player.max_hearts):
            color = C_HEART if i < player.hearts else (80, 40, 40)
            # jednoduché srdce jako dva kruhy + trojúhelník
            pygame.draw.circle(screen, color, (sx + i*35 - 5, 20), 8)
            pygame.draw.circle(screen, color, (sx + i*35 + 5, 20), 8)
            pts = [(sx+i*35-12, 22), (sx+i*35+12, 22), (sx+i*35, 34)]
            pygame.draw.polygon(screen, color, pts)
            # outline
            pygame.draw.circle(screen, C_BLACK, (sx + i*35 - 5, 20), 8, 1)
            pygame.draw.circle(screen, C_BLACK, (sx + i*35 + 5, 20), 8, 1)
            pygame.draw.polygon(screen, C_BLACK, pts, 1)

        # Kosti (malé puntíky)
        bx = 240
        bones_per_heart = 6
        for i in range(player.max_hearts * bones_per_heart):
            color = C_BONE if i < player.bones else (60, 50, 40)
            col = i % bones_per_heart
            row = i // bones_per_heart
            pygame.draw.circle(screen, color, (bx + col*12, 16 + row*14), 4)

        # Skóre
        score_surf = self.font_big.render(f"{player.score:08d}", True, (255, 220, 80))
        screen.blit(score_surf, (SCREEN_W - score_surf.get_width() - 16, 10))

        # State debug (lze vypnout)
        state_surf = self.font_small.render(player.state, True, (120, 120, 120))
        screen.blit(state_surf, (SCREEN_W // 2 - state_surf.get_width() // 2, 52))
