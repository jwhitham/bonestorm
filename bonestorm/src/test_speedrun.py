import typing
import pygame
import os
from pathlib import Path

from .constants import *
from .game_types import *
from .director import Director
from .limits import get_counter_limit, get_allowed_counter
from .game_config import GameConfig
from .time_conv import time_conv

def test_speedrun(frames_per_move: int) -> int:
    assert frames_per_move > 0
    level_id = 1
    total_counter_for_earlier_levels = 0

    print(f"Frames per move = {frames_per_move}")

    while level_id <= 100:
        game_config = GameConfig(level_id, 0)
        counter_limit = get_counter_limit(total_counter_for_earlier_levels, level_id)
        allowed = get_allowed_counter(level_id)
        print(f"Level {level_id} w {game_config.width} h {game_config.height} v {game_config.num_values} "
              f"t {time_conv(counter_limit)} total {time_conv(total_counter_for_earlier_levels)} "
              f"of {time_conv(allowed)}: ", end="", flush=True)
        
        assert game_config.num_values <= MAX_NUM_VALUES

        best: typing.Optional[int] = None
        for i in range(game_config.num_values):
            counter = Director(game_config).speedrun(i, frames_per_move, counter_limit)
            if (counter is not None) and ((best is None) or (counter < best)):
                best = counter

        if best is None:
            print("unable to solve")
            return 0

        counter = best
        print(f"solved in {time_conv(counter)}")
        total_counter_for_earlier_levels += counter
        level_id += 1
    return 0
