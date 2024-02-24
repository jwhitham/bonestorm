import typing
from pygame import Rect

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant
from ..colour import Colour
from ..font import Font
from ..images import Images
from ..draw_button import draw_button

from .base import BaseState


class IntermissionState(BaseState):
    def __init__(self, variant: Variant, game_database: GameDatabase) -> None:
        BaseState.__init__(self, variant, game_database)
        self.buttons: typing.List[typing.Tuple[str,
                    typing.Callable[[int], BaseState], int]] = []
        self.buttons_rects: typing.List[Rect] = []
        self.info_messages: typing.List[str] = []
        self.headline = ""
        self.info_area_horizontal_align = 0

    def draw(self, screen_area: SurfaceType, mouse_pos: ScreenXY, images: Images, font: Font) -> None:
        screen_rect = screen_area.get_rect()

        # Determine space usage on the screen
        margin = max(1, min(screen_rect.width, screen_rect.height) // self.variant.constants.MARGIN_DIVISOR)
        headline_height = max(1, (screen_rect.height - (margin * 4)) // 5)
        buttons_height = max(1, ((screen_rect.height - (margin * 4)) // 20) * len(self.buttons))

        # Black margins
        screen_area.fill(self.variant.palette.WINDOW_BG)

        # draw headline
        headline_rect = Rect(margin, margin, screen_rect.width - (margin * 2), headline_height)
        headline_area = screen_area.subsurface(headline_rect)
        headline_area.fill(self.variant.palette.HEADLINE_BG)
        font.draw(text_area=headline_area,
                  text=self.headline,
                  colour=Colour(*self.variant.palette.HEADLINE_FG))

        # draw buttons
        buttons_rect = Rect(headline_rect)
        buttons_rect.height = buttons_height
        buttons_rect.bottom = screen_rect.height - margin
        buttons_area = screen_area.subsurface(buttons_rect)
        self.draw_buttons(screen_area, buttons_rect, mouse_pos, font)

        # draw info box in the remaining space
        info_rect = Rect(headline_rect)
        info_rect.height = screen_rect.height - buttons_rect.height - headline_rect.height - (margin * 4)
        info_rect.top = headline_rect.bottom + margin
        screen_area.subsurface(info_rect).fill(self.variant.palette.INFO_BG)
        
        # Text area is slightly smaller
        info_rect.width -= margin
        info_rect.centerx = headline_rect.centerx
        self.draw_info(screen_area.subsurface(info_rect), images, font)

    def draw_info(self, info_area: SurfaceType, images: Images, font: Font) -> None:
        font.draw(text_area=info_area, text='\n'.join(self.info_messages),
                  colour=Colour(*self.variant.palette.INFO_FG),
                  horizontal_align=self.info_area_horizontal_align)

    def draw_buttons(self, screen_area: SurfaceType, buttons_rect: Rect,
                     mouse_pos: ScreenXY, font: Font) -> None:

        # Decide on positioning for buttons while drawing them
        button_outer_rect = Rect(buttons_rect)
        button_outer_rect.height = buttons_rect.height // len(self.buttons)

        self.buttons_rects.clear()
        for (text, callback, arg) in self.buttons:
            self.buttons_rects.append(Rect(button_outer_rect))

            if text != "":
                draw_button(screen_area=screen_area,
                        button_outer_rect=button_outer_rect,
                        text=text,
                        mouse_pos=mouse_pos,
                        font=font,
                        variant=self.variant)

            button_outer_rect.top = button_outer_rect.bottom

    def click(self, xy: ScreenXY) -> BaseState:
        for (button_rect, (text, callback, arg)) in zip(self.buttons_rects, self.buttons):
            if button_rect.collidepoint(xy):
                return callback(arg)
        return self

    def play_level(self, level_id: int) -> BaseState:
        from .begin import BeginState
        return BeginState(self.variant, self.game_database, level_id)

    def return_to_title(self, _: int) -> BaseState:
        from .title import TitleState
        return TitleState(self.variant, self.game_database)

    def no_button(self, _: int) -> BaseState:
        return self

    def how_to_play(self, _: int) -> BaseState:
        from .help import HelpState
        return HelpState(self.variant, self.game_database)
