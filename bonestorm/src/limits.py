import typing

from .constants import *

def get_counter_limit(total_counter_for_earlier_levels: int, level_id: int) -> int:
    # Return the time that's available for completing level_id
    # Here is the total time allowed for levels 1 .. level_id
    allowed_counter = get_allowed_counter(level_id)
    return max(0, allowed_counter - total_counter_for_earlier_levels)

def get_allowed_counter(level_id: int) -> int:
    # Return the time that's allowed for completing levels 1 .. level_id
    return (level_id * PLAYER_ADD_PER_LEVEL_FRAMES) + PLAYER_INITIAL_FRAMES
