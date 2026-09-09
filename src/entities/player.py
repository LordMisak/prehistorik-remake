# player.py — Player FSM: stavy, fyzika, kolize, animace (placeholder)

import pygame
from src.core.settings import *


# Stavy hráče
class State:
    IDLE         = "idle"
    WALK         = "walk"
    RUN          = "run"
    JUMP         = "jump"
    FALL         = "fall"
    ATTACK       = "attack"
    ATTACK_UP    = "attack_up"
    ATTACK_DOWN  = "attack_down"
    HIT          = "hit"
    DEAD         = "dead"
    CROUCH       = "crouch"
    CROUCH_ATTACK = "crouch_attack"


class Player:
    WIDTH  = 28
    HEIGHT = 48

    def __init__(self, x: float, y: float):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vx = 0.0
        self.vy = 0.0

        self.state    = State.IDLE
        self.facing   = 1      # 1 = vpravo, -1 = vlevo
        self.on_ground = False

        # Zdraví
        self.hearts = 3
        self.bones  = 18      # 3 srdce * 6 kostí
        self.max_hearts = 3
        self.max_bones  = 18

        # Lives
        self.lives = 3
        self.score = 0

        # Coyote time + jump buffer
        self.coyote_timer  = 0
        self.jump_buffer   = 0

        # Útok
        self.attack_timer  = 0
        self.ATTACK_FRAMES = 15    # snímků trvá útok
        self.attack_dir    = (1, 0)

        # Zásah (blikání po hit)
        self.hit_timer     = 0
        self.HIT_FRAMES    = 40
        self.invincible    = False

        # Animace
        self.anim_tick     = 0
        self.run_streak    = 0   # počet snímků nepřetržitého běhu

    # ------------------------------------------------------------------ INPUT

    def handle_input(self, keys):
        if self.state in (State.DEAD, State.HIT):
            return

        left  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        up    = keys[pygame.K_UP]    or keys[pygame.K_w]
        down  = keys[pygame.K_DOWN]  or keys[pygame.K_s]
        atk   = keys[pygame.K_SPACE]

        crouching = down and self.on_ground

        # Pohyb (ne během útoku)
        if self.state not in (State.ATTACK, State.CROUCH_ATTACK):
            if crouching:
                self.vx = 0
                self._set_state(State.CROUCH)
            else:
                if left:
                    self.facing = -1
                    spd = PLAYER_RUN_SPEED if self.run_streak > 60 else PLAYER_SPEED
                    self.vx = -spd
                elif right:
                    self.facing = 1
                    spd = PLAYER_RUN_SPEED if self.run_streak > 60 else PLAYER_SPEED
                    self.vx = spd
                else:
                    self.vx = 0

                # Počítáme run streak
                if (left or right) and self.on_ground:
                    self.run_streak += 1
                else:
                    self.run_streak = max(0, self.run_streak - 2)

        # Skok
        if up:
            self.jump_buffer = JUMP_BUFFER_TIME

        # Útok
        if atk and self.state not in (State.ATTACK, State.CROUCH_ATTACK, State.DEAD):
            if crouching:
                self._set_state(State.CROUCH_ATTACK)
            elif up:
                self._set_state(State.ATTACK_UP)
                self.attack_dir = (0, -1)
            elif down and not self.on_ground:
                self._set_state(State.ATTACK_DOWN)
                self.attack_dir = (0, 1)
            else:
                self._set_state(State.ATTACK)
                self.attack_dir = (self.facing, 0)

    # ------------------------------------------------------------------ UPDATE

    def update(self, tilemap):
        self.anim_tick += 1

        # Coyote time
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Jump buffer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.coyote_timer > 0 and self.vy >= 0:
                self.vy = JUMP_POWER
                self.coyote_timer = 0
                self.jump_buffer  = 0
                self._set_state(State.JUMP)

        # Timery
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0 and self.state in (
                State.ATTACK, State.ATTACK_UP, State.ATTACK_DOWN, State.CROUCH_ATTACK
            ):
                self._set_state(State.IDLE)

        if self.hit_timer > 0:
            self.hit_timer -= 1
            self.invincible = True
            if self.hit_timer == 0:
                self.invincible = False
                if self.state == State.HIT:
                    self._set_state(State.IDLE)

        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # Pohyb + kolize
        self._move_and_collide(tilemap)

        # Aktualizace stavu pohybem
        if self.state not in (
            State.ATTACK, State.ATTACK_UP, State.ATTACK_DOWN,
            State.CROUCH_ATTACK, State.DEAD, State.HIT, State.CROUCH
        ):
            if not self.on_ground:
                self._set_state(State.JUMP if self.vy < 0 else State.FALL)
            elif abs(self.vx) > 0.1:
                if self.run_streak > 60:
                    self._set_state(State.RUN)
                else:
                    self._set_state(State.WALK)
            else:
                self._set_state(State.IDLE)

        # Smrt pádem do propasti
        if self.rect.top > 3000:
            self.die()

    # ------------------------------------------------------------------ KOLIZE

    def _move_and_collide(self, tilemap):
        from src.world.tilemap import TILE_SIZE, TILE_LETHAL

        self.on_ground = False

        # X pohyb
        self.rect.x += int(self.vx)
        self._resolve_x(tilemap)

        # Y pohyb
        self.rect.y += int(self.vy)
        self._resolve_y(tilemap)

    def _resolve_x(self, tilemap):
        from src.world.tilemap import TILE_SIZE
        ts = TILE_SIZE
        for row in range(self.rect.top // ts, (self.rect.bottom - 1) // ts + 1):
            if self.vx > 0:
                col = self.rect.right // ts
                if tilemap.is_solid(col, row):
                    self.rect.right = col * ts
                    self.vx = 0
            elif self.vx < 0:
                col = (self.rect.left - 1) // ts
                if tilemap.is_solid(col, row):
                    self.rect.left = (col + 1) * ts
                    self.vx = 0

    def _resolve_y(self, tilemap):
        from src.world.tilemap import TILE_SIZE
        ts = TILE_SIZE
        if self.vy > 0:
            row = self.rect.bottom // ts
            for col in range(self.rect.left // ts, (self.rect.right - 1) // ts + 1):
                t = tilemap.get(col, row)
                if tilemap.is_solid(col, row):
                    self.rect.bottom = row * ts
                    self.vy = 0
                    self.on_ground = True
                    break
                elif tilemap.is_lethal(col, row):
                    self.die()
        elif self.vy < 0:
            row = (self.rect.top - 1) // ts
            for col in range(self.rect.left // ts, (self.rect.right - 1) // ts + 1):
                if tilemap.is_solid(col, row):
                    self.rect.top = (row + 1) * ts
                    self.vy = 0
                    break

    # ------------------------------------------------------------------ HIT / SMRT

    def take_damage(self, amount: int = 6):
        """Ztratí 'amount' kostí. Srdce se ubývají automaticky."""
        if self.invincible:
            return False
        self.bones -= amount
        if self.bones <= 0:
            self.hearts -= 1
            self.bones = self.max_bones if self.hearts > 0 else 0
        if self.hearts <= 0:
            self.die()
        else:
            self.hit_timer = self.HIT_FRAMES
            self._set_state(State.HIT)
        return True

    def die(self):
        self.lives -= 1
        self._set_state(State.DEAD)

    @property
    def is_dead(self) -> bool:
        return self.state == State.DEAD

    # ------------------------------------------------------------------ ATTACK HITBOX

    def get_attack_rect(self) -> pygame.Rect | None:
        """Vrátí obdélník útoku nebo None pokud neútočí."""
        if self.state not in (State.ATTACK, State.ATTACK_UP, State.ATTACK_DOWN, State.CROUCH_ATTACK):
            return None
        # Pouze první polovina animace útoku je aktivní
        if self.attack_timer < self.ATTACK_FRAMES // 2:
            return None
        dx, dy = self.attack_dir
        reach = 40
        cx, cy = self.rect.centerx, self.rect.centery
        ax = cx + dx * (self.WIDTH // 2 + reach // 2)
        ay = cy + dy * (self.HEIGHT // 2 + reach // 2)
        return pygame.Rect(ax - 20, ay - 20, 40, 40)

    # ------------------------------------------------------------------ DRAW

    def draw(self, screen: pygame.Surface, camera):
        # Blikání při zásahu
        if self.invincible and (self.anim_tick // 4) % 2 == 0:
            return

        sr = camera.apply(self.rect)

        # Tělo — placeholder obdélník
        body_color = C_PLAYER
        if self.state == State.HIT:
            body_color = C_RED
        elif self.state == State.DEAD:
            body_color = (100, 100, 100)
        elif self.state == State.CROUCH:
            body_color = (200, 160, 80)

        # Dřep — nižší postava
        if self.state in (State.CROUCH, State.CROUCH_ATTACK):
            cr = pygame.Rect(sr.x, sr.y + sr.h // 2, sr.w, sr.h // 2)
            pygame.draw.rect(screen, body_color, cr, border_radius=6)
            pygame.draw.rect(screen, C_PLAYER_OUT, cr, 2, border_radius=6)
        else:
            pygame.draw.rect(screen, body_color, sr, border_radius=6)
            pygame.draw.rect(screen, C_PLAYER_OUT, sr, 2, border_radius=6)

        # Oči
        eye_x = sr.centerx + self.facing * 5
        pygame.draw.circle(screen, C_BLACK, (eye_x, sr.top + 12), 4)
        pygame.draw.circle(screen, C_WHITE, (eye_x, sr.top + 12), 2)

        # Kyj (útok)
        if self.state in (State.ATTACK, State.ATTACK_UP, State.ATTACK_DOWN):
            dx, dy = self.attack_dir
            kx = sr.centerx + dx * 30
            ky = sr.centery  + dy * 30
            pygame.draw.line(screen, C_PLAYER_OUT, (sr.centerx, sr.centery), (kx, ky), 6)
            pygame.draw.circle(screen, (150, 100, 50), (kx, ky), 10)
            pygame.draw.circle(screen, C_PLAYER_OUT, (kx, ky), 10, 2)

        # Debug: attack hitbox
        # atk = self.get_attack_rect()
        # if atk:
        #     pygame.draw.rect(screen, (255,0,0), camera.apply(atk), 2)

    # ------------------------------------------------------------------ HELPERS

    def _set_state(self, new_state: str):
        if self.state == new_state:
            return
        # Útok — nastavit timer
        if new_state in (State.ATTACK, State.ATTACK_UP, State.ATTACK_DOWN, State.CROUCH_ATTACK):
            self.attack_timer = self.ATTACK_FRAMES
        self.state = new_state
