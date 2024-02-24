import typing
import pygame
from pygame import Rect

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase, UpdateEffect
from ..variant import Variant
from ..font import Font
from ..images import Images
from ..director import Director, ClickEffect
from ..colour import Colour
from ..game_config import GameConfig
from ..deterministic_random import DeterministicRandom
from ..time_conv import time_conv
from ..draw_button import draw_button

from .base import BaseState


class GamePlayState(BaseState):
    def __init__(self, variant: Variant, game_database: GameDatabase,
                level_id: int, counter_limit: int) -> None:
        BaseState.__init__(self, variant, game_database)

        # Create level
        self.game_config = GameConfig(level_id, self.game_database.get_seed_for_level(level_id))
        self.old_play_info = self.game_database.get_play_info_for_level(level_id)
        self.move_made = False
        self.images_filtered = False
        self.counter = 0
        self.counter_limit = counter_limit
        self.score = 0
        self.combo = 0
        self.director = Director(self.game_config)
        self.game_rect: RectType = Rect(0, 0, 1, 1)
        self.back_button_rect: RectType = Rect(1, 1, 1, 1)

    def update(self) -> BaseState:
        if self.counter >= self.counter_limit:
            # Run out of time
            self.game_database.failed_attempt_at_level(level_id=self.game_config.level_id)
            from .end import EndState
            return EndState(variant=self.variant,
                            game_database=self.game_database,
                            level_id=self.game_config.level_id,
                            update_effect=UpdateEffect.OUT_OF_TIME,
                            old_play_info=self.old_play_info,
                            score=self.score, counter=self.counter)
        if self.move_made:
            self.counter += 1
            self.director.update()
        return self

    def draw(self, screen_area: SurfaceType, mouse_pos: ScreenXY, images: Images, font: Font) -> None:
        if not self.images_filtered:
            images.prepare(self.game_config)
            self.images_filtered = True

        screen_area.fill(self.variant.palette.WINDOW_BG)
        screen_rect = screen_area.get_rect()

        is_landscape = (screen_rect.width > screen_rect.height)

        # Bottom line area allocated
        bottom_line_rect = Rect(screen_rect)
        bottom_line_rect.height = screen_rect.height // self.variant.constants.BACK_BUTTON_HEIGHT_DIVISOR
        bottom_line_rect.bottom = screen_rect.bottom

        # Back button occupies some (landscape) or all (portrait) of the bottom line
        self.back_button_rect = Rect(bottom_line_rect)
        self.back_button_rect.width = screen_rect.width // self.variant.constants.BACK_BUTTON_WIDTH_DIVISOR

        # Score area is on the bottom line (landscape) or above it (portrait)
        score_area_rect = Rect(bottom_line_rect)
        if is_landscape:
            score_area_rect.width -= self.back_button_rect.width * 2
            score_area_rect.center = bottom_line_rect.center
        else:
            score_area_rect.height = screen_rect.height // self.variant.constants.SCORE_AREA_PORTRAIT_HEIGHT_DIVISOR
            score_area_rect.bottom = bottom_line_rect.top

        # Game area is above the score area
        expanded_game_rect = Rect(screen_rect)
        expanded_game_rect.height = score_area_rect.top

        # Draw game area
        cell_size = min(expanded_game_rect.width // self.game_config.width,
                     expanded_game_rect.height // self.game_config.height)
        self.game_rect = Rect(0, 0, cell_size * self.game_config.width, cell_size * self.game_config.height)
        self.game_rect.center = expanded_game_rect.center
        self.director.draw(screen_area.subsurface(self.game_rect), images)

        # Draw back button: \u2190 is left arrow
        draw_button(screen_area=screen_area,
                button_outer_rect=self.back_button_rect,
                text=f" \u2190 Back",
                mouse_pos=mouse_pos,
                font=font,
                variant=self.variant)

        # Score and other status information
        time_left = self.counter_limit - self.counter
        if self.move_made:
            score_text = [
                f"SCORE {self.score}",
                f"COMBO {self.combo}",
                f"TIME {time_conv(time_left)}"]
        else:
            score_text = [
                self.variant.text.CLICK_TO_START,
                f"LEVEL {self.game_config.level_id}",
                f"TIME {time_conv(time_left)}"]

        if ((time_left > (FRAME_RATE_HZ * 10)) or ((time_left % 10) < 5)):
            score_colour = Colour(*self.variant.palette.SCORE_FG)
        else:
            score_colour = Colour(*self.variant.palette.SCORE_TIME_OUT_FG)

        font.draw(screen_area.subsurface(score_area_rect),
                  text="   ".join(score_text) if is_landscape else "\n".join(score_text),
                  colour=score_colour,
                  horizontal_align=0 if is_landscape else -1,
                  vertical_align=0 if is_landscape else 1)


    def click(self, xy: ScreenXY) -> BaseState:
        click_effect = self.director.click(self.game_rect, xy)
        if click_effect == ClickEffect.OUTSIDE_GAME:
            if self.back_button_rect.collidepoint(xy):
                return self.cancel()
            return self

        self.move_made = True

        # Marks are awarded for neatness and accuracy (but not speed)
        if click_effect == ClickEffect.LOCK_GOOD:
            self.combo = max(self.combo + 1, 1)
            self.score = max(self.score + self.combo, 1)
        elif click_effect == ClickEffect.LOCK_BAD:
            self.combo = 0
            self.score = max(self.score - 1, 0)
        else:
            # Neutral
            self.score = max(self.score + 1, 1)

        # Game continues until completed
        if not self.director.is_complete():
            return self

        update_effect = self.game_database.successful_attempt_at_level(
                        level_id=self.game_config.level_id,
                        score=self.score, counter=self.counter)
        from .end import EndState
        return EndState(variant=self.variant,
                        game_database=self.game_database,
                        level_id=self.game_config.level_id,
                        update_effect=update_effect,
                        old_play_info=self.old_play_info,
                        score=self.score, counter=self.counter)

    def cancel(self) -> BaseState:
        self.game_database.failed_attempt_at_level(level_id=self.game_config.level_id)
        from .begin import BeginState
        return BeginState(self.variant, self.game_database, self.game_config.level_id)
