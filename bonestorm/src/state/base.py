from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant
from ..font import Font
from ..images import Images

class BaseState:
    quit_flag = False

    def __init__(self, variant: Variant, game_database: GameDatabase) -> None:
        self.variant = variant
        self.game_database = game_database

    def draw(self, screen_area: SurfaceType, mouse_pos: ScreenXY, images: Images, font: Font) -> None:
        pass

    def click(self, xy: ScreenXY) -> "BaseState":
        return self

    def update(self) -> "BaseState":
        return self 

    def cancel(self) -> "BaseState":
        return self
