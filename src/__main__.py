import json
import arcade
import sys 
import os

import constants
from gui.views import MainMenuView
from gui.utils import load_settings

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

def ensure_settings_file() -> None:
    if not constants.SETTINGS_DIR.exists():
        constants.SETTINGS_DIR.mkdir(parents=True)

    path = constants.SETTINGS_DIR / "saved_settings.json"
    if not path.exists():
        with open(path, "w") as f:
            json.dump(constants.DEFAULT_SETTINGS, f, indent=2)

def main() -> None:
    ensure_settings_file()
    settings = load_settings()
    try:
        size = settings["window_size_dropdown"]
        if size:
            width, height = map(int, size.split("x"))
        else:
            width, height = arcade.get_display_size()
    except (KeyError, TypeError):
        width, height = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT

    window = arcade.Window(
        width=width,
        height=height,
        title=constants.SCREEN_TITLE,
        center_window=True,
        fullscreen=True,
    )

    main_menu = MainMenuView(
        settings.get("current_level", 1),
    )
    window.show_view(main_menu)
    main_menu.setup()
    window.run()


if __name__ == "__main__":
    main()