import typing
import random
from pygame import Rect

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant
from ..font import Font
from ..images import Images
from ..time_conv import time_conv
from ..game_config import GameConfig
from ..colour import Colour
from ..deterministic_random import DeterministicRandom

from .base import BaseState
from .begin_or_end import BeginOrEndState


class BeginState(BeginOrEndState):
    def __init__(self, variant: Variant, game_database: GameDatabase, level_id: int) -> None:
        BeginOrEndState.__init__(self, variant, game_database, level_id)

        self.headline = f"  Level {level_id}  "
        if self.play_info.best_counter is not None:
            self.info_messages.append(f"Best Time {time_conv(self.play_info.best_counter)} - "
                                      f"Score {self.play_info.last_score} - ")
            if self.play_info.completed > 1:
                self.info_messages[-1] += f"Completed {self.play_info.completed} times"
            else:
                self.info_messages[-1] += "Completed once"
        elif self.play_info.played > 1:
            self.info_messages.append(f"Attempted {self.play_info.played} times so far")
        elif self.play_info.played == 1:
            self.info_messages.append("Attempted once so far")
        else:
            self.info_messages.append("New level!")

        self.info_messages.append("")

        seed = self.game_database.get_seed_for_level(level_id)
        self.game_config = GameConfig(level_id, seed)
        self.info_messages.append(f"{self.game_config.width} \u2715 {self.game_config.height} - ")
        if seed:
            self.info_messages[-1] += f"Seed {seed:04X} - "
        self.info_messages[-1] += f"Time Limit {time_conv(self.get_counter_limit())}"
        self.images_filtered = False

    def add_seed_button(self) -> None:
        seed = self.game_database.get_seed_for_level(self.level_id)
        if seed:
            self.buttons.append(("Reset random seed to 0", self.reset_seed, 0))
        else:
            self.buttons.append(("Generate new random seed", self.generate_seed, 0))

    def reset_seed(self, _: int) -> BaseState:
        self.game_database.set_seed_for_level(self.level_id, 0)
        return BeginState(self.variant, self.game_database, self.level_id)

    def generate_seed(self, _: int) -> BaseState:
        seed = random.Random().randrange(1, 0x10000)
        self.game_database.set_seed_for_level(self.level_id, seed)
        return BeginState(self.variant, self.game_database, self.level_id)

    def draw_info(self, info_area: SurfaceType, images: Images, font: Font) -> None:
        info_rect = info_area.get_rect()

        # Icons showing the level sequence appear at the bottom
        icon_sub_rect = Rect(info_rect)
        icon_sub_rect.height = min(info_rect.height // 2, 
                # twice the height of a cell image
                2 * (info_rect.width // ((self.game_config.num_values * 2) + 1)))
        icon_sub_rect.bottom = info_rect.bottom

        # The info text appears above that
        colour = Colour(*self.variant.palette.INFO_FG)
        info_sub_rect = Rect(info_rect)
        info_sub_rect.height = info_rect.height - icon_sub_rect.height
        info_sub_area = info_area.subsurface(info_sub_rect)

        # Draw info text
        font.draw(text_area=info_sub_area, text='\n'.join(self.info_messages), colour=colour)

        if not self.images_filtered:
            images.prepare(self.game_config)
            self.images_filtered = True

        # Draw icons
        cell_image_size = min(icon_sub_rect.width // ((self.game_config.num_values * 2) + 1),
                              (icon_sub_rect.height * 2) // 3)
        whole_cell_rect = Rect(0, 0,
                               cell_image_size * ((self.game_config.num_values * 2) + 1),
                               cell_image_size)
        whole_cell_rect.centerx = icon_sub_rect.centerx
        whole_cell_rect.top = icon_sub_rect.top
        one_cell_rect = Rect(0, 0, cell_image_size, cell_image_size)
        one_cell_rect.topleft = whole_cell_rect.topleft

        # Draw icons
        for i in range(self.game_config.num_values):
            one_cell_rect.left = one_cell_rect.right
            images.draw(value=i, game_area=info_area, cell_rect=one_cell_rect)
            one_cell_rect.left = one_cell_rect.right

        # Draw some arrows
        # \u21b1 is up then right arrow
        one_arrow_rect = Rect(0, 0, cell_image_size, cell_image_size // 2)
        one_arrow_rect.left = whole_cell_rect.left
        one_arrow_rect.centery = whole_cell_rect.centery
        font.draw(text_area=info_area.subsurface(one_arrow_rect), text="\u21b1", colour=colour)
        one_arrow_rect.left = one_arrow_rect.right
        one_arrow_rect.left = one_arrow_rect.right

        # \u2192 is right arrow
        for i in range(self.game_config.num_values - 1):
            font.draw(text_area=info_area.subsurface(one_arrow_rect), text="\u2192", colour=colour)
            one_arrow_rect.left = one_arrow_rect.right
            one_arrow_rect.left = one_arrow_rect.right

        # \u21b4 is right then down arrow
        font.draw(text_area=info_area.subsurface(one_arrow_rect), text="\u21b4", colour=colour)

        # Return arrows
        # \u2190 is left arrow
        one_arrow_rect.left = whole_cell_rect.left
        one_arrow_rect.top = whole_cell_rect.bottom
        for i in range(self.game_config.num_values):
            one_arrow_rect.left = one_arrow_rect.right
            font.draw(text_area=info_area.subsurface(one_arrow_rect),
                      text="\u2190", colour=colour)
            one_arrow_rect.left = one_arrow_rect.right
