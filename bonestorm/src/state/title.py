import typing

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant
from ..font import Font
from ..images import Images
from ..time_conv import time_conv

from .base import BaseState
from .intermission import IntermissionState


class TitleState(IntermissionState):
    def __init__(self, variant: Variant, game_database: GameDatabase) -> None:
        IntermissionState.__init__(self, variant, game_database)

        self.headline = variant.text.TITLE

        recent_played = self.game_database.get_most_recent_level_played()
        max_completed = self.game_database.get_maximum_level_completed()

        (total_score, total_counter) = self.game_database.get_score_and_time_up_to_and_including_level(max_completed)

        if variant.text.GREETING:
            self.info_messages.append(variant.text.GREETING)
            self.info_messages.append("")

        if max_completed > 0:
            self.info_messages.append(f"Complete level {max_completed + 1}")
            self.info_messages.append("to unlock more levels!")
            self.info_messages.append("")
            self.info_messages.append(f"Your total score is {total_score}.")
            self.info_messages.append("")
            if max_completed > 1:
                self.info_messages.append(f"Your time is {time_conv(total_counter)}")
                self.info_messages.append(f"for levels 1 .. {max_completed}.")
            self.buttons.append((f"Go To New Level {max_completed + 1}", self.play_level, max_completed + 1))
        else:
            self.info_messages.append("")
            self.info_messages.append("Click 'Go To Level 1' to Play!")
            self.info_messages.append("")

        self.buttons.append(("How To Play", self.how_to_play, 0))

        if 1 < recent_played < max_completed:
            self.buttons.append((f"Go To Level {recent_played}", self.play_level, recent_played))

        self.buttons.append(("Go To Level 1", self.play_level, 1))

    def cancel(self) -> BaseState:
        from .quit import QuitState
        return QuitState(self.variant, self.game_database)
