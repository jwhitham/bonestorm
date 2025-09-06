from .constants import *

class GameConfig:
    def __init__(self, level_id: int, seed: int) -> None:
        self.level_id = level_id
        self.seed = seed
        self.width = min(15, ((level_id + 1) // 3) + 3)
        self.height = min(10, ((level_id - 1) // 3) + 3)
        self.num_values = min(5, (level_id // 6) + 3)
        if self.level_id >= 50:
            # difficulty increased
            self.num_values = min(MAX_NUM_VALUES, self.num_values + ((level_id - 50) // 5))

