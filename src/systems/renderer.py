# renderer.py — procedurální grafika inspirovaná Prehistorik 2
# Kreslí tile, hráče, pozadí pomocí pygame.draw (bez externích obrázků)

import pygame
import math
import random
from src.core.settings import TILE_SIZE


# ---------------------------------------------------------------------------
# PALETA (věrná originálu)
# ---------------------------------------------------------------------------
SKY_TOP    = (100, 160, 210)
SKY_BOT    = (160, 200, 230)
FLAME_COL  = (240, 240, 220)   # bílé "plameny" na horizontu
MTN_DARK   = (40,  45,  55)    # vzdálené hory
MTN_MID    = (65,  70,  85)
MTN_LIGHT  = (90,  95, 110)
STONE_DARK = (80,  65,  50)
STONE_MID  = (110, 90,  65)
STONE_LITE = (140, 120, 90)
STONE_HIGH = (160, 140, 105)
MOSS_DARK  = (40,  90,  40)
MOSS_LITE  = (70,  140, 55)
SKIN       = (210, 160, 100)
SKIN_DARK  = (170, 120, 70)
HAIR       = (100, 60,  20)
CLUB       = (120, 80,  40)
CLUB_HEAD  = (90,  60,  30)
HUD_BG     = (15,  12,  8)
HUD_BORDER = (60,  50,  35)
HEART_RED  = (220, 50,  50)
HEART_DARK = (80,  20,  20)
SCORE_COL  = (240, 200, 80)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)


# ---------------------------------------------------------------------------
# POZADÍ — obloha + "plameny" + horské siluety
# ---------------------------------------------------------------------------
class Background:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        rng = random.Random(42)
        self.flame_pts = []
        # Horizon vysoko — hory jsou v horní třetině obrazovky
        horizon = int(screen_h * 0.35)
        for x in range(0, screen_w + 20, 6):
            y = horizon + rng.randint(-12, 12)
            self.flame_pts.append((x, y))

        # Horské siluety — základna je na horizontu
        self.mtns = [
            self._gen_mountains(screen_w, horizon + 10, 160, 8,  rng, seed=1),
            self._gen_mountains(screen_w, horizon + 5,  110, 12, rng, seed=2),
            self._gen_mountains(screen_w, horizon,       70, 18, rng, seed=3),
        ]
        self.mtn_colors = [MTN_DARK, MTN_MID, MTN_LIGHT]

    def _gen_mountains(self, w, base_y, peak_h, spacing, rng, seed):
        rng2 = random.Random(seed)
        pts = [(0, base_y)]
        x = 0
        while x < w + spacing * 2:
            x += rng2.randint(spacing, spacing * 2)
            y = base_y - rng2.randint(peak_h // 2, peak_h)
            pts.append((x, y))
        pts.append((w + spacing * 2, base_y))
        pts.append((w + spacing * 2, base_y + 100))
        pts.append((0, base_y + 100))
        return pts

    def draw(self, screen: pygame.Surface, camera_x: float):
        # Obloha — pouze horní část (nad horizontem)
        horizon_px = int(self.h * 0.35)
        for y in range(horizon_px):
            t = y / horizon_px
            r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.w, y))

        # Pod horizontem — tmavě šedá skalní stěna (jako v originále)
        pygame.draw.rect(screen, (55, 58, 68), (0, horizon_px, self.w, self.h - horizon_px))

        # "Plameny" na horizontu — bílé zubaté linie
        if len(self.flame_pts) >= 2:
            pygame.draw.lines(screen, FLAME_COL, False, self.flame_pts, 3)
            shifted = [(x, y+4) for x, y in self.flame_pts]
            pygame.draw.lines(screen, (210, 210, 190), False, shifted, 2)

        # Horské siluety (parallax různou rychlostí)
        speeds = [0.05, 0.12, 0.2]
        for i, (pts, col, spd) in enumerate(zip(self.mtns, self.mtn_colors, speeds)):
            ox = int(camera_x * spd) % (self.w + 200)
            shifted = [(x - ox, y) for x, y in pts]
            pygame.draw.polygon(screen, col, shifted)
            shifted2 = [(x - ox + self.w + 200, y) for x, y in pts]
            pygame.draw.polygon(screen, col, shifted2)


# ---------------------------------------------------------------------------
# TILE RENDERER — kamenné bloky s texturou
# ---------------------------------------------------------------------------
def draw_stone_tile(screen: pygame.Surface, rx: int, ry: int, ts: int):
    """Kamenný blok — základ + světlé a tmavé plochy pro 3D efekt."""
    r = pygame.Rect(rx, ry, ts, ts)
    pygame.draw.rect(screen, STONE_MID, r)

    # Světlý levý+horní okraj (highlight)
    pygame.draw.line(screen, STONE_LITE, (rx, ry), (rx+ts-1, ry), 2)
    pygame.draw.line(screen, STONE_LITE, (rx, ry), (rx, ry+ts-1), 2)
    # Tmavý pravý+dolní okraj (shadow)
    pygame.draw.line(screen, STONE_DARK, (rx+ts-1, ry), (rx+ts-1, ry+ts-1), 2)
    pygame.draw.line(screen, STONE_DARK, (rx, ry+ts-1), (rx+ts-1, ry+ts-1), 2)

    # Nepravidelné kameny uvnitř (crack efekt)
    rng = random.Random(rx * 1000 + ry)
    for _ in range(2):
        cx = rx + rng.randint(4, ts-8)
        cy = ry + rng.randint(4, ts-8)
        cw = rng.randint(4, 10)
        ch = rng.randint(3, 7)
        pygame.draw.rect(screen, STONE_HIGH, (cx, cy, cw, ch))
        pygame.draw.rect(screen, STONE_DARK, (cx, cy, cw, ch), 1)


def draw_grass_tile(screen: pygame.Surface, rx: int, ry: int, ts: int):
    """Tráva/mech navrchu kamenného bloku."""
    draw_stone_tile(screen, rx, ry, ts)
    # Zelený pruh navrchu
    pygame.draw.rect(screen, MOSS_DARK, (rx, ry, ts, 7))
    pygame.draw.rect(screen, MOSS_LITE, (rx, ry, ts, 4))
    # Malé stébla trávy
    rng = random.Random(rx + ry * 137)
    for _ in range(4):
        gx = rx + rng.randint(2, ts-4)
        pygame.draw.line(screen, MOSS_LITE, (gx, ry), (gx + rng.randint(-2,2), ry - rng.randint(3,6)), 1)


def draw_oneway_tile(screen: pygame.Surface, rx: int, ry: int, ts: int):
    """One-way platforma — tenký kamenný blok s mechem."""
    pygame.draw.rect(screen, STONE_MID, (rx, ry, ts, ts//2))
    pygame.draw.rect(screen, MOSS_DARK, (rx, ry, ts, 5))
    pygame.draw.rect(screen, MOSS_LITE, (rx, ry, ts, 3))
    pygame.draw.rect(screen, STONE_DARK, (rx, ry, ts, ts//2), 1)


# ---------------------------------------------------------------------------
# HRÁČ — jeskynní člověk (pygame.draw, bez spritů)
# ---------------------------------------------------------------------------
class PlayerRenderer:
    def draw(self, screen: pygame.Surface, player, camera):
        from src.entities.player import State
        sr = camera.apply(player.rect)

        # Blikání při zásahu
        if player.invincible and (player.anim_tick // 4) % 2 == 0:
            return

        facing = player.facing
        cx = sr.centerx
        state = player.state
        tick = player.anim_tick

        # Dřep — nižší pozice
        if state in (State.CROUCH, State.CROUCH_ATTACK):
            self._draw_crouching(screen, cx, sr.bottom, facing, tick)
        elif state == State.DEAD:
            self._draw_dead(screen, cx, sr.bottom, facing)
        elif state == State.HIT:
            self._draw_standing(screen, cx, sr.bottom, facing, tick, tint=(255, 100, 100))
        else:
            walk_anim = state in (State.WALK, State.RUN)
            self._draw_standing(screen, cx, sr.bottom, facing, tick, walk_anim=walk_anim)

        # Kyj při útoku
        if state in (State.ATTACK,):
            self._draw_club_side(screen, cx, sr.bottom - 28, facing)
        elif state == State.ATTACK_UP:
            self._draw_club_up(screen, cx, sr.bottom - 28)
        elif state == State.ATTACK_DOWN:
            self._draw_club_down(screen, cx, sr.bottom - 28)

    def _draw_standing(self, screen, cx, bot, facing, tick, walk_anim=False, tint=None):
        # Animace chůze — přesouvá nohy
        leg_off = int(math.sin(tick * 0.25) * 5) if walk_anim else 0
        body_col = tint if tint else SKIN

        # Nohy
        pygame.draw.rect(screen, SKIN_DARK, (cx - 10, bot - 16, 8, 16))   # levá noha
        pygame.draw.rect(screen, SKIN_DARK, (cx + 2,  bot - 16 + leg_off, 8, 16))  # pravá noha
        # Boty (tmavé)
        pygame.draw.rect(screen, (60, 40, 20), (cx - 12, bot - 5, 10, 5))
        pygame.draw.rect(screen, (60, 40, 20), (cx + 1, bot - 5 + leg_off, 10, 5))

        # Tělo (kůže + kožešinový "kostým")
        pygame.draw.ellipse(screen, body_col, (cx - 13, bot - 38, 26, 22))
        pygame.draw.rect(screen, (100, 70, 40), (cx - 10, bot - 28, 20, 12))  # pás

        # Hlava
        pygame.draw.circle(screen, body_col, (cx + facing * 2, bot - 44), 13)
        pygame.draw.circle(screen, SKIN_DARK, (cx + facing * 2, bot - 44), 13, 1)

        # Vlasy
        pygame.draw.arc(screen, HAIR,
            pygame.Rect(cx - 12 + facing*2, bot - 58, 24, 20),
            0, math.pi, 5)

        # Oko
        eye_x = cx + facing * 6
        pygame.draw.circle(screen, BLACK, (eye_x, bot - 45), 3)
        pygame.draw.circle(screen, WHITE, (eye_x + facing, bot - 46), 1)

        # Nos
        pygame.draw.circle(screen, SKIN_DARK, (cx + facing * 9, bot - 42), 2)

        # Úsměv / grimasa (při HIT tint)
        if tint:
            pygame.draw.arc(screen, BLACK,
                pygame.Rect(cx + facing*2 - 6, bot - 40, 12, 6),
                math.pi, 2*math.pi, 2)  # otočený = grimasa
        else:
            pygame.draw.arc(screen, BLACK,
                pygame.Rect(cx + facing*2 - 5, bot - 39, 10, 5),
                0, math.pi, 2)

        # Ruka s kyjíkem (idle/walk)
        arm_x = cx - facing * 8
        pygame.draw.line(screen, SKIN, (cx - facing*4, bot-30), (arm_x, bot-22), 4)
        pygame.draw.line(screen, CLUB, (arm_x, bot-22), (arm_x - facing*6, bot-10), 5)
        pygame.draw.circle(screen, CLUB_HEAD, (arm_x - facing*6, bot-8), 7)
        pygame.draw.circle(screen, BLACK, (arm_x - facing*6, bot-8), 7, 1)

    def _draw_crouching(self, screen, cx, bot, facing, tick):
        # Dřepící postava — kompaktnější
        pygame.draw.rect(screen, SKIN_DARK, (cx - 10, bot - 10, 8, 10))
        pygame.draw.rect(screen, SKIN_DARK, (cx + 2,  bot - 10, 8, 10))
        pygame.draw.ellipse(screen, SKIN, (cx - 13, bot - 26, 26, 18))
        pygame.draw.circle(screen, SKIN, (cx + facing*2, bot - 32), 12)
        eye_x = cx + facing * 6
        pygame.draw.circle(screen, BLACK, (eye_x, bot - 33), 3)

    def _draw_dead(self, screen, cx, bot, facing):
        # Ležící postava
        pygame.draw.ellipse(screen, SKIN_DARK, (cx - 20, bot - 12, 40, 12))
        pygame.draw.circle(screen, SKIN, (cx + facing*14, bot - 10), 10)
        pygame.draw.line(screen, BLACK, (cx + facing*10, bot-12), (cx+facing*18, bot-8), 2)
        pygame.draw.line(screen, BLACK, (cx + facing*12, bot-8), (cx+facing*16, bot-12), 2)

    def _draw_club_side(self, screen, cx, arm_y, facing):
        # Kyj napřažený do strany
        start = (cx + facing * 5, arm_y)
        end   = (cx + facing * 38, arm_y - 5)
        pygame.draw.line(screen, SKIN, (cx, arm_y), start, 5)
        pygame.draw.line(screen, CLUB, start, end, 6)
        pygame.draw.circle(screen, CLUB_HEAD, end, 9)
        pygame.draw.circle(screen, BLACK, end, 9, 2)

    def _draw_club_up(self, screen, cx, arm_y):
        end = (cx + 5, arm_y - 35)
        pygame.draw.line(screen, CLUB, (cx, arm_y), end, 6)
        pygame.draw.circle(screen, CLUB_HEAD, end, 9)
        pygame.draw.circle(screen, BLACK, end, 9, 2)

    def _draw_club_down(self, screen, cx, arm_y):
        end = (cx + 5, arm_y + 25)
        pygame.draw.line(screen, CLUB, (cx, arm_y), end, 6)
        pygame.draw.circle(screen, CLUB_HEAD, end, 9)
        pygame.draw.circle(screen, BLACK, end, 9, 2)


# ---------------------------------------------------------------------------
# HUD — dole, styl originálu
# ---------------------------------------------------------------------------
class HUDRenderer:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.font_lbl  = pygame.font.Font(None, 22)
        self.font_val  = pygame.font.Font(None, 28)
        self.bar_h = 36

    def draw(self, screen: pygame.Surface, player):
        by = self.h - self.bar_h

        # Černý pruh dole
        pygame.draw.rect(screen, HUD_BG, (0, by, self.w, self.bar_h))
        pygame.draw.rect(screen, HUD_BORDER, (0, by, self.w, 2))

        # --- LIVES ---
        lbl = self.font_lbl.render("LIVES", True, (160, 140, 100))
        screen.blit(lbl, (10, by + 4))
        # Ikonka hlavy
        hx, hy = 10, by + 18
        pygame.draw.circle(screen, SKIN, (hx + 6, hy), 7)
        pygame.draw.circle(screen, HAIR, (hx + 6, hy - 4), 5)
        pygame.draw.circle(screen, BLACK, (hx + 9, hy - 1), 2)
        # Počet
        lives_surf = self.font_val.render(f"x{player.lives}", True, WHITE)
        screen.blit(lives_surf, (hx + 16, hy - 8))

        # --- SCORE ---
        slbl = self.font_lbl.render("SCORE", True, (160, 140, 100))
        sx = self.w // 2 - 50
        screen.blit(slbl, (sx, by + 4))
        score_surf = self.font_val.render(f"{player.score:08d}", True, SCORE_COL)
        screen.blit(score_surf, (sx, by + 18))

        # --- ENERGY (srdíčka) ---
        ex = self.w - 120
        elbl = self.font_lbl.render("ENERGY", True, (160, 140, 100))
        screen.blit(elbl, (ex, by + 4))
        for i in range(player.max_hearts):
            hcol = HEART_RED if i < player.hearts else HEART_DARK
            hcx = ex + i * 32 + 12
            hcy = by + 24
            # Srdíčko = dva kruhy + trojúhelník
            pygame.draw.circle(screen, hcol, (hcx - 5, hcy), 7)
            pygame.draw.circle(screen, hcol, (hcx + 5, hcy), 7)
            pygame.draw.polygon(screen, hcol, [(hcx-11, hcy+4), (hcx+11, hcy+4), (hcx, hcy+14)])
            # Outline
            pygame.draw.circle(screen, BLACK, (hcx-5, hcy), 7, 1)
            pygame.draw.circle(screen, BLACK, (hcx+5, hcy), 7, 1)
            pygame.draw.polygon(screen, BLACK, [(hcx-11, hcy+4), (hcx+11, hcy+4), (hcx, hcy+14)], 1)
