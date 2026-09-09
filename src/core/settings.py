# settings.py — všechny konstanty na jednom místě

# Okno
SCREEN_W = 1280
SCREEN_H = 720
TITLE = "Prehistorik Remake"
FPS = 60

# Fyzika
GRAVITY = 0.6
MAX_FALL_SPEED = 18
JUMP_POWER = -14
PLAYER_SPEED = 4
PLAYER_RUN_SPEED = 7
COYOTE_TIME = 6          # snímků po pádu stále lze skočit
JUMP_BUFFER_TIME = 8     # snímků předem stisknutého skoku

# Tile mapa
TILE_SIZE = 32

# Barvy (placeholder grafika)
C_SKY        = (135, 180, 220)
C_GROUND     = (100, 70, 40)
C_GRASS      = (60, 140, 50)
C_PLAYER     = (230, 180, 100)
C_PLAYER_OUT = (80, 50, 20)
C_ENEMY      = (200, 80, 80)
C_COIN       = (255, 220, 50)
C_HUD_BG     = (30, 20, 10, 180)
C_WHITE      = (255, 255, 255)
C_BLACK      = (0, 0, 0)
C_RED        = (220, 50, 50)
C_HEART      = (220, 60, 60)
C_BONE       = (240, 235, 220)

# Vrstvy rendrování (z-order)
LAYER_BG      = 0
LAYER_TILES   = 10
LAYER_ITEMS   = 20
LAYER_ENEMIES = 30
LAYER_PLAYER  = 40
LAYER_FX      = 50
LAYER_HUD     = 60
