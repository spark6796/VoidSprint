from pathlib import Path
import sys

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "VoidSprint"

# Path to the game's root directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    ROOT_DIR = Path(sys.executable).parent
    ASSETS_DIR = ROOT_DIR / "_internal/assets"
else:
    # Running as Python script
    ROOT_DIR = Path(__file__).parent.parent.resolve()
    ASSETS_DIR = ROOT_DIR / "assets"

# Path to the game's assets directory
# we don't need to be strict here as ROOT
# if the user is in the wrong dir they will already get
# the error from above
ASSETS_DIR = Path(ASSETS_DIR)
FONTS_DIR = ASSETS_DIR / "fonts"
SAVES_DIR = Path("saves").resolve()
SETTINGS_DIR = SAVES_DIR / "settings"
DEFAULT_SETTINGS = {
    "window_size_dropdown": None,
    "current_level": 1,
}

TILE_SCALING = 3

# --- Constants for player movement and physics ---

# Character scale and position
CHARACTER_SCALING = 2.5
CHARACTER_POSITION = (128, 128)

# Gravity
GRAVITY = 2000

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.4
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.5

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied to move player left/right
PLAYER_MOVE_FORCE_ON_GROUND = 8000
PLAYER_MOVE_FORCE_IN_AIR = 2000
PLAYER_JUMP_IMPULSE = 2000
PLAYER_SMALL_JUMP_IMPULSE = 1500

# --- Constants for player ends here ---


# --- Constants for enemy movement and physics ---

# Enemy scale
ENEMY_SCALING = 4
ENEMY_FRICTION = 0.5
ENEMY_MASS = 2.0

ARROW_MOVE_FORCE = 120
ARROW_MASS = 0.1
ARROW_GRAVITY = 10

SMALL_FIREBALL_MOVE_FORCE = 150
SMALL_FIREBALL_MASS = 0.1
SMALL_FIREBALL_GRAVITY = 15

LARGE_FIREBALL_MOVE_FORCE = 150
LARGE_FIREBALL_MASS = 0.1
LARGE_FIREBALL_GRAVITY = 15

ENEMY_PLAYER_DISTANCE_THRESHOLD = 300
ENEMY_ATTACK_DISTANCE_THRESHOLD = 100
ENEMY_ATTACK_PROBABILITY = 5

ENEMY_MOVE_FORCE = 500

# --- Constants for enemy ends here ---