import arcade

from constants import ASSETS_DIR


class RoguelikeInterior:
    def __init__(self) -> None:
        self.path = ASSETS_DIR / "roguelike-interior.png"
        self.spritesheet = arcade.load_spritesheet(self.path)
        self.tile_size = 16
        self.spacing = 1
        self.sprites: dict[str, arcade.Texture] = {
            "potted-plant-1": self.get_tile(16, 0),
            "potted-plant-2": self.get_tile(17, 0),
            "white-candelabra": self.get_tile(19, 0),
            "white-candelabra-lit": self.get_tile(19, 1),
            "yellow-candelabra": self.get_tile(20, 0),
            "yellow-candelabra-lit": self.get_tile(20, 1),
        }

    def get_sprite(self, name: str) -> arcade.Texture:
        return self.sprites[name]

    def get_tile(self, x: int, y: int) -> arcade.Texture:
        x_pos = x * self.tile_size + x * self.spacing
        y_pos = y * self.tile_size + y * self.spacing

        rect = arcade.Rect(
            x_pos,                    
            x_pos + self.tile_size,  
            y_pos,                    
            y_pos + self.tile_size,   
            self.tile_size,           
            self.tile_size,           
            x_pos,                    
            y_pos                     
        )
        return self.spritesheet.get_texture(
            rect,
            y_up=True
        )

class RoguelikeBase:
    def __init__(self) -> None:
        self.path = ASSETS_DIR / "roguelike-base.png"
        self.spritesheet = arcade.load_spritesheet(self.path)
        self.tile_size = 16
        self.spacing = 1

    def get_tile(self, x: int, y: int) -> arcade.Texture:
        rect = arcade.Rect(
            x,                      
            x + self.tile_size,       
            y,                       
            y + self.tile_size,       
            self.tile_size,           
            self.tile_size,           
            x,                        
            y 
        )
        return self.spritesheet.get_texture(
          rect
        )