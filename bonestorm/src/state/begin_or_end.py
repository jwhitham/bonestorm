import typing

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant
from ..font import Font
from ..images import Images
from ..limits import get_counter_limit

from .base import BaseState
from .intermission import IntermissionState


class BeginOrEndState(IntermissionState):
    def __init__(self, variant: Variant, game_database: GameDatabase, level_id: int) -> None:
        IntermissionState.__init__(self, variant, game_database)

        self.level_id = level_id
        max_completed = self.game_database.get_maximum_level_completed()

        self.play_info = self.game_database.get_play_info_for_level(self.level_id)

        if level_id == max_completed:
            self.buttons.append((f"Go To New Level {level_id + 1}", self.play_level, level_id + 1))
        elif level_id < max_completed:
            self.buttons.append((f"Go To Next Level {level_id + 1}", self.play_level, level_id + 1))

        if self.play_info.completed > 0:
            self.buttons.append((f"Replay Level {level_id}", self.game_start, 0))
        elif self.play_info.played > 0:
            self.buttons.append((f"Play Level {level_id} Again", self.game_start, 0))
        else:
            self.buttons.append((f"Play New Level {level_id}", self.game_start, 0))

        self.add_seed_button()

        if level_id > 1:
            self.buttons.append((f"Go To Level {level_id - 1}", self.play_level, level_id - 1))
        else:
            self.buttons.append(("How To Play", self.how_to_play, 0))

        self.buttons.append(("Go to Title Screen", self.return_to_title, 0))

    def add_seed_button(self) -> None:
        pass

    def cancel(self) -> BaseState:
        return self.return_to_title(0)

    def game_start(self, _: int) -> BaseState:
        from .game_play import GamePlayState
        return GamePlayState(self.variant, self.game_database, self.level_id, self.get_counter_limit())

    def get_counter_limit(self) -> int:
        (_, total_counter_for_earlier_levels) = self.game_database.get_score_and_time_up_to_and_including_level(self.level_id - 1)
        return get_counter_limit(total_counter_for_earlier_levels, self.level_id)
