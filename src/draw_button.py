import typing

from .game_types import *
from .variant import Variant
from .colour import Colour
from .font import Font


def draw_button(screen_area: SurfaceType, button_outer_rect: RectType,
                text: str, mouse_pos: ScreenXY, font: Font,
                variant: Variant) -> None:
    button_inner_rect = button_outer_rect.inflate(-3, -3)
    button_text_rect = button_inner_rect.inflate(-3, -3)

    if button_text_rect.height < 1 or button_text_rect.width < 1:
        # Sanity check: button is too small and won't be drawn
        return

    button_inner_area = screen_area.subsurface(button_inner_rect)
    button_inner_area.fill(variant.palette.BUTTON_EDGE_FG)

    button_text_area = screen_area.subsurface(button_text_rect)
    button_text_area.fill(variant.palette.BUTTON_BG)

    colour = Colour(*variant.palette.BUTTON_FG)
    if button_inner_rect.collidepoint(mouse_pos):
        colour = Colour(*variant.palette.BUTTON_ACTIVE_FG)

    font.draw(text_area=button_text_area, text=text, colour=colour)
