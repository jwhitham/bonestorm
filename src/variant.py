from pathlib import Path
import json
import typing

from .game_types import *

def decode_colour(colour: str) -> ColourType:
    if (len(colour) != 7) or not colour.startswith("#"):
        raise ValueError("Colour should be in '#xxxxxx' form")

    return (int(colour[1:3], 16),
            int(colour[3:5], 16),
            int(colour[5:7], 16))

class Palette:
    def __init__(self) -> None:
        self.WINDOW_BG = decode_colour("#252623")
        self.HEADLINE_BG = decode_colour("#d0b17a")
        self.HEADLINE_FG = decode_colour("#131210")
        self.INFO_BG = decode_colour("#997646")
        self.INFO_FG = decode_colour("#080808")
        self.BUTTON_FG = decode_colour("#f0f0f0")
        self.BUTTON_ACTIVE_FG = decode_colour("#f0f000")
        self.BUTTON_EDGE_FG = decode_colour("#867672")
        self.BUTTON_BG = decode_colour("#463632")
        self.SCORE_FG = decode_colour("#40a040")
        self.SCORE_TIME_OUT_FG = decode_colour("#f04040")

class Text:
    def __init__(self) -> None:
        self.GREETING = ""
        self.TITLE = "   Bone Storm   "
        self.CLICK_TO_START = "CLICK TO START"

class Constants:
    def __init__(self) -> None:
        self.MARGIN_DIVISOR = 20
        self.DESKTOP = True
        self.SCORE_AREA_PORTRAIT_HEIGHT_DIVISOR = 6
        self.BACK_BUTTON_WIDTH_DIVISOR = 8
        self.BACK_BUTTON_HEIGHT_DIVISOR = 25
        self.FORCE_WIDTH = 0
        self.FORCE_HEIGHT = 0

class Variant:
    def __init__(self, file_name: Path) -> None:
        with open(file_name, "rt", encoding="utf-8") as fd:
            contents = json.load(fd)

        self.palette = Palette()
        palette = contents.get("palette", {})
        for name in palette:
            if hasattr(self.palette, name):
                setattr(self.palette, name, decode_colour(palette[name]))

        self.text = Text()
        text = contents.get("text", {})
        for name in text:
            if hasattr(self.text, name):
                setattr(self.text, name, str(text[name]))

        self.constants = Constants()
        constants = contents.get("constants", {})
        for name in constants:
            if hasattr(self.constants, name):
                if isinstance(getattr(self.constants, name), bool):
                    setattr(self.constants, name, bool(int(constants[name])))
                else:
                    setattr(self.constants, name, int(constants[name]))
