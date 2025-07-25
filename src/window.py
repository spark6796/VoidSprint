import time
import json
import typing as t

import arcade
import arcade.gui
from arcade.types import Color

import tileset
from gui.views import main_menu
from gui.views.pause_menu import PauseMenu
from components.sprites.enemy import Enemy, EnemyTypes
from components.sprites.player import Player
from constants import (
    SETTINGS_DIR,
    CHARACTER_POSITION,
    CHARACTER_SCALING,
    DEFAULT_DAMPING,
    ENEMY_FRICTION,
    ENEMY_MASS,
    ENEMY_SCALING,
    GRAVITY,
    PLAYER_FRICTION,
    PLAYER_MASS,
    PLAYER_MAX_HORIZONTAL_SPEED,
    PLAYER_MAX_VERTICAL_SPEED,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    TILE_SCALING,
    WALL_FRICTION,
)


class GameView(arcade.View):
    _instance: t.Optional["GameView"] = None

    def __new__(cls, *args, **kwargs) -> "GameView":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        current_level: int,
    ) -> None:
        super().__init__()
        self.current_level = current_level
        self.window.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BLACK)
        arcade.SpriteList.DEFAULT_TEXTURE_FILTER = (0x2600,0x2600)
        self.spritesheet = tileset.RoguelikeInterior()
        self.base_spritesheet = tileset.RoguelikeBase()

        self.object_lists: dict[str, list[arcade.types.TiledObject]] = {}
        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=DEFAULT_DAMPING,
            gravity=(0, -GRAVITY),
        )

        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()

        self.reset()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        
        self.pause_menu = PauseMenu(self, self.camera_sprites)

    def go_to_main_menu(self) -> None:
        view = main_menu.MainMenuView(
            self.current_level,
        )
        view.setup()
        self.window.set_mouse_visible(True)
        self.window.show_view(view)

    def setup_enemies(self) -> list[arcade.Sprite]:
        enemies = []
        for enemy in self.object_lists.get("Enemies", []):
            if not enemy.name:
                continue
            points: arcade.types.PointList = enemy.shape  # type: ignore
            x, y = points[0][0] - 24, points[0][1]
            sprite = Enemy(
                enemy_type=EnemyTypes[enemy.name.upper()],
                scene=self.scene,
                position=(int(x), int(y)),
                scale=ENEMY_SCALING,
                properties=enemy.properties,
            )
            enemies.append(sprite)
        return enemies
    
    def setup_doors(self) -> arcade.SpriteList:
        door_sprites = arcade.SpriteList()
        door_textures = {
            'spawn': {'x':561,'y':68},
            'next': {'x':595,'y':68}
        }
        for door in self.object_lists.get('Doors',[]):
            if door.name not in ['spawn','next']:
                continue
            x, y = door.shape[0][0] + 26 , door.shape[0][1] - 24 # type: ignore
            door_texture_x , door_texture_y = door_textures[door.name]['x'],door_textures[door.name]['y']
            door_texture = self.base_spritesheet.get_tile(door_texture_x,door_texture_y)
            sprite = arcade.Sprite(door_texture)
            sprite.position = (int(x), int(y))
            sprite.scale = TILE_SCALING
            sprite.properties = door.properties # type: ignore
            door_sprites.append(sprite)
        self.scene.add_sprite_list('Doors',sprite_list=door_sprites)
        return door_sprites

    def create_scene(self) -> arcade.Scene:
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Gold": {"use_spatial_hash": True},
        }
        tile_map = arcade.load_tilemap(
            f"assets/level-{self.current_level}-map.tmx",
            scaling=TILE_SCALING,
            layer_options=layer_options,
            lazy=True,
        )

        if tile_map.background_color:
            self.background_color = Color.from_iterable(tile_map.background_color)

        self.object_lists = tile_map.object_lists

        return arcade.Scene.from_tilemap(tile_map)

    def reset(self) -> None:
        self.scene = self.create_scene()
        try:
            spawn_door = [door for door in self.object_lists.get('Doors',[]) if door.name == 'spawn'][0]
            spawn_x, spawn_y = spawn_door.shape[0][0], spawn_door.shape[0][1] # type: ignore
        except Exception:
            spawn_x, spawn_y = CHARACTER_POSITION
        self.player_sprite = Player(
            scene=self.scene, position=(spawn_x, spawn_y), scale=CHARACTER_SCALING # type: ignore
        )
        self.enemy_sprites = self.setup_enemies()
        self.door_sprites = self.setup_doors()
        p_sprites = self.physics_engine.sprites.copy()
        for sprite in p_sprites:
            self.physics_engine.remove_sprite(sprite)
        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
        )
        self.physics_engine.add_sprite_list(
            self.scene["Platforms"],
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )
        self.physics_engine.add_sprite_list(
            self.enemy_sprites,
            mass=ENEMY_MASS,
            friction=ENEMY_FRICTION,
            moment_of_inertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="enemy",
            body_type=arcade.PymunkPhysicsEngine.DYNAMIC,
        )
        self.physics_engine.add_sprite_list(
            self.door_sprites,
            mass=0,
            friction=0,
            collision_type="door",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )
        try:
            self.scene.remove_sprite_list_by_name("Enemies")
            self.scene.remove_sprite_list_by_name("Player")
            self.scene.remove_sprite_list_by_name("Bars")
        except KeyError:
            pass
        self.scene.add_sprite_list("Enemies")
        self.scene["Enemies"].extend(self.enemy_sprites)
        self.scene.add_sprite_list("Player")
        self.scene["Player"].append(self.player_sprite)
        self.scene.add_sprite_list("Bars")
        self.scene["Bars"].append(self.player_sprite.health_bar)
        self.scene["Bars"].append(self.player_sprite.stamina_bar)

        def player_enemy_collision_handler(player: Player, enemy: Enemy, *_: t.Any) -> None:
            if player.attacking:
                if enemy._damage_value != 0 or (enemy._last_hit_time and time.monotonic() - enemy._last_hit_time < 0.5):  # type: ignore
                    return
                enemy._last_hit_time = time.monotonic()  # type: ignore
                enemy._damage_value = player.attack_power  # type: ignore
                enemy.hurt = True
            if enemy.attacking:
                enemy_id = id(enemy)
                if enemy_id in player._hit_map and time.monotonic() - player._hit_map[enemy_id] < 0.5:  # type: ignore
                    return
                player._hit_map[enemy_id] = time.monotonic()  # type: ignore
                player._damage_map[id(enemy)] = enemy.spritesheet.attack_power  # type: ignore
                player.hurt = True

        self.physics_engine.add_collision_handler(
            "player", "enemy", post_handler=player_enemy_collision_handler
        )

        def player_door_collision_handler(player: Player, door: arcade.Sprite, *_: t.Any) -> bool:
            if door.properties['type'] == 'next':
                self.current_level += 1
                self.update_level()
                self.reset()
            return False

        self.physics_engine.add_collision_handler(
            "player",
            "door",
            pre_handler=player_door_collision_handler,
        )

    def update_level(self) -> None:
        with open(SETTINGS_DIR / "saved_settings.json", "r") as f:
            settings = json.load(f)
        settings["current_level"] = self.current_level
        with open(SETTINGS_DIR / "saved_settings.json", "w") as f:
            json.dump(settings, f, indent=2)

    def on_draw(self) -> None:
        self.clear()

        self.camera_sprites.use()
        self.scene.draw()
        score_text = self.player_sprite.score
        cx, cy = self.camera_sprites.top_right
        score_text.position = (cx - 150, cy - 50)
        score_text.draw()
        if self.pause_menu.paused:
            self.pause_menu.draw()

        self.manager.draw()
        
        return
        
        # Draw platforms, the player, and the gold to channel0
        # self.channel0.use()
        # self.channel0.clear()
        # self.camera_sprites.use()
        # self.scene["Player"].draw()
        # self.scene["Platforms"].draw()

        # # Draw everything else to channel1
        # self.channel1.use()
        # self.channel1.clear()
        # self.camera_sprites.use()
        # self.scene.draw()
        # score_text = self.player_sprite.score
        # cx, cy = self.camera_sprites.top_right
        # score_text.position = (cx - 150, cy - 50)
        # score_text.draw()

        # # Draw the player to channel2
        # self.channel2.use()
        # self.channel2.clear()
        # self.camera_sprites.use()
        # self.scene["Player"].draw()

        # self.window.use()

        # self.shadertoy.render()

        # if self.pause_menu.paused:
        #     self.pause_menu.draw()

        # self.manager.draw()

    def draw_title(self) -> None:
        text = arcade.Text(
            SCREEN_TITLE,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            color=arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
        )
        text.draw()

    def on_key_press(self, key: int, _: int) -> None:
        if key == arcade.key.ESCAPE:
            self.pause_menu.toggle_pause()
        else:
            self.player_sprite.on_key_press(key, _)

    def on_key_release(self, key: int, _: int) -> None:
        self.player_sprite.on_key_release(key, _)

    def center_camera_to_player(self) -> None:
        screen_center_x = self.player_sprite.center_x
        screen_center_y = self.player_sprite.center_y

        if screen_center_x - self.window.width / 2 < 0:
            screen_center_x = self.window.width / 2
        if screen_center_y - self.window.height / 2 < 0:
            screen_center_y = self.window.height / 2

        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position,
            player_centered,
            0.1,
        )

    def on_update(self, delta_time: float) -> None:
        if self.pause_menu.paused:
            return
        if self.player_sprite.is_dead:
            self.go_to_main_menu()
            return
        self.scene.update(delta_time)
        self.scene.update_animation(delta_time)
        self.physics_engine.step()

        self.center_camera_to_player()

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self.camera_sprites.match_screen(and_projection=True)
        self.camera_gui.match_screen(and_projection=True)
        self.manager.on_resize(width, height)