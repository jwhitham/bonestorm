import typing

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase, UpdateEffect, PlayInfo
from ..variant import Variant
from ..font import Font
from ..images import Images
from ..limits import get_allowed_counter
from ..time_conv import time_conv

from .base import BaseState
from .begin_or_end import BeginOrEndState


class EndState(BeginOrEndState):
    def __init__(self, variant: Variant, game_database: GameDatabase,
                 level_id: int, update_effect: UpdateEffect,
                 old_play_info: PlayInfo, score: int, counter: int) -> None:
        BeginOrEndState.__init__(self, variant, game_database, level_id)
        
        text_wall: typing.List[str] = []

        if update_effect != UpdateEffect.OUT_OF_TIME:
            self.headline = f"  Level {level_id} Complete  "
            self.info_messages.append(f"Score {score}")
            self.info_messages.append(f"Time {time_conv(counter)}")
            self.info_messages.append("")
        else:
            self.headline = f"  Level {level_id} Failed  "

        if update_effect == UpdateEffect.COMPLETED_FIRST_TIME:
            self.info_messages.append("Congratulations!")
            self.info_messages.append(f"Level {level_id + 1} is unlocked!")

        elif update_effect == UpdateEffect.OUT_OF_TIME:
            self.headline = f"Level {level_id} Failed"
            self.info_messages.clear()
            text_wall.append(
                    f"You ran out of time. You have now played this level {self.play_info.played} times.")
            text_wall.append("")
            if level_id > 1:
                text_wall.append("To get more time for this level, complete earlier levels")
                (_, total_counter) = self.game_database.get_score_and_time_up_to_and_including_level(level_id - 1)
                text_wall.append(
                    f"faster. Your total time for levels 1 .. {level_id - 1} is {time_conv(total_counter)},")
                text_wall.append(
                    f"leaving only {time_conv(self.get_counter_limit())} for this level, as the total time")
                text_wall.append(
                    f"allowed for levels 1 .. {level_id} is {time_conv(get_allowed_counter(level_id))}.")
            else:
                text_wall.append("Select 'Replay Level 1' to try again or 'How To Play' for instructions.")

        else:
            text_wall.append(f"You have now completed this level {self.play_info.completed} times.")
            text_wall.append("")
            if update_effect == UpdateEffect.BETTER_TIME_AND_SCORE:
                text_wall.append(f"You've improved your time and score!")
            elif update_effect == UpdateEffect.BETTER_TIME:
                text_wall.append(f"You've improved your time!")
            elif update_effect == UpdateEffect.BETTER_SCORE:
                text_wall.append(f"You've improved your score!")
            elif update_effect == UpdateEffect.NO_IMPROVEMENT:
                text_wall.append(f"Sorry, no improvement on your previous result this time.")

            if old_play_info.best_counter is not None:
                if update_effect in [UpdateEffect.BETTER_TIME_AND_SCORE, UpdateEffect.BETTER_TIME]:
                    text_wall.append(f"Your time improved from {time_conv(old_play_info.best_counter)} "
                                              f"to {time_conv(counter)}.")
                else:
                    text_wall.append(f"Best time {time_conv(old_play_info.best_counter)}: "
                                              f"this attempt was {time_conv(counter)}.")
            if old_play_info.last_score is not None:
                if update_effect in [UpdateEffect.BETTER_TIME_AND_SCORE, UpdateEffect.BETTER_SCORE]:
                    text_wall.append(f"Your score improved from {old_play_info.last_score} to {score}.")
                else:
                    text_wall.append(f"Best score {old_play_info.last_score}: "
                                              f"this attempt was {score}.")
        if text_wall:
            self.info_messages.append(" ".join(text_wall))
