import typing

from .game_types import *

class Colour:
    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b

    def get_rgb(self) -> ColourType:
        return (self.r, self.g, self.b)

    def brighten(self, brightness: int) -> "Colour":
        return Colour(max(self.r, brightness),
                      max(self.g, brightness),
                      max(self.b, brightness))

    def darken(self, darkness: int) -> "Colour":
        return Colour(max(0, self.r - darkness),
                      max(0, self.g - darkness),
                      max(0, self.b - darkness))
