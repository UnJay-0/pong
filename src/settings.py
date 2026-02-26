import json, pygame
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent.parent / 'config' / 'settings.json'

DEFAULT_SETTINGS = {
    "resolution": [800, 500],
    "field_dimensions": [[0, 800], [100, 500]],
    "fullscreen": False,
    "music_volume": 0.6,
    "sfx_volume": 0.8,
    "keybindings": {
        "first_player": {
            "up": pygame.K_w,
            "down": pygame.K_s
        },
        "second_player": {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN
        },
        "ui_movement": {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "confirm": pygame.K_KP_ENTER
        }
    },
}

def load_settings() -> dict:
    """
    Loads the settings.
    If the settings file does not exists or does not contain specific keys
    those will be overwritten by the default settings.

    Returns
    -------
    dict
        settings for the game and application.
    """
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"path: {SETTINGS_PATH}")
    if SETTINGS_PATH.exists():
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS | data
        return merged
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """
    Save the settings given.

    Parameters
    ----------
    settings: dict
        settings to be saved
    """
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
