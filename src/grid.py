
import enum
import typing
from pygame import Rect

from .game_types import *
from .deterministic_random import DeterministicRandom
from .images import Images
from .game_config import GameConfig

class Cell:
    def __init__(self, xy: GridXY, num_values: int, value: int) -> None:
        self.xy = xy
        self.num_values = num_values
        self.hidden_value = value
        self.lock_value = self.hidden_value
        self.locked = False

    def update(self, add: int) -> None:
        self.hidden_value = (self.hidden_value + add) % self.num_values
        if not self.locked:
            self.lock_value = self.hidden_value

    def toggle(self) -> None:
        self.locked = not self.locked

    def get_lock_group(self) -> int:
        if not self.locked:
            return -1
        else:
            return self.lock_value

    def get_value(self) -> int:
        return self.lock_value

    def is_locked(self) -> bool:
        return self.locked

class ClickEffect(enum.Enum):
    OUTSIDE_GAME = enum.auto()
    UNLOCK = enum.auto()
    LOCK_NEUTRAL = enum.auto()
    LOCK_BAD = enum.auto()
    LOCK_GOOD = enum.auto()

class Grid:
    def __init__(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        self.game_config = game_config

        self.cells: typing.Dict[GridXY, Cell] = {}
        for y in range(self.game_config.height):
            for x in range(self.game_config.width):
                self.cells[(x, y)] = Cell(
                    xy=(x, y),
                    num_values=self.game_config.num_values,
                    value=rng.randrange(0, self.game_config.num_values))

        self.lock_groups: typing.Dict[int, typing.Set[Cell]] = {}
        for lock_group in range(-1, self.game_config.num_values):
            self.lock_groups[lock_group] = set()
        for cell in self.cells.values():
            self.lock_groups[cell.get_lock_group()].add(cell)

        self.periodic_counter = 0

    def is_complete(self) -> bool:
        size = self.game_config.width * self.game_config.height
        for lock_group in range(0, self.game_config.num_values):
            if len(self.lock_groups[lock_group]) == size:
                return True

        return False

    def get_cell(self, xy: GridXY) -> typing.Optional[Cell]:
        return self.cells.get(xy, None)

    def get_largest_lock_group(self) -> typing.Optional[int]:
        largest_group_size = 0
        for lock_group in range(0, self.game_config.num_values):
            largest_group_size = max(largest_group_size, len(self.lock_groups[lock_group]))
        largest_group_count = 0
        largest_lock_group = -1
        for lock_group in range(0, self.game_config.num_values):
            if largest_group_size == len(self.lock_groups[lock_group]):
                largest_group_count += 1
                largest_lock_group = lock_group

        if largest_group_count != 1:
            # There is no single largest group
            return None
        else:
            return largest_lock_group

    def toggle(self, xy: GridXY) -> ClickEffect:
        cell = self.cells.get(xy, None)
        if cell is None:
            return ClickEffect.OUTSIDE_GAME

        # Remove from old lock group
        old_lock_group = cell.get_lock_group()
        self.lock_groups[old_lock_group].remove(cell)

        # Assess the size of the lock groups, ignoring the affected cell
        largest_lock_group = self.get_largest_lock_group()

        # Apply the change
        cell.toggle()

        # Add to new lock group
        new_lock_group = cell.get_lock_group()
        self.lock_groups[new_lock_group].add(cell)

        if new_lock_group < 0:
            return ClickEffect.UNLOCK

        # Now a cell became locked - how does this affect the score?
        if largest_lock_group is None:
            # There is no single largest group, so we don't know if this is a good move or not
            return ClickEffect.LOCK_NEUTRAL
        elif largest_lock_group == new_lock_group:
            # Joined the largest lock group
            return ClickEffect.LOCK_GOOD
        else:
            # Joined a different lock group
            return ClickEffect.LOCK_BAD

    def update(self, xy: GridXY, add: int) -> None:
        cell = self.cells.get(xy, None)
        if cell is not None:
            cell.update(add)

    def get_cell_size(self, game_rect: RectType) -> int:
        return max(1, min(game_rect.width // self.game_config.width,
                        game_rect.height // self.game_config.height))

    def get_cell_rect(self, game_rect: RectType, xy: GridXY) -> RectType:
        (x, y) = xy
        cell_size = self.get_cell_size(game_rect)
        return Rect((x * cell_size) + game_rect.left,
                    (y * cell_size) + game_rect.top,
                    cell_size, cell_size)

    def click(self, game_rect: RectType, xy: ScreenXY) -> ClickEffect:
        cell_size = self.get_cell_size(game_rect)
        (sx, sy) = xy
        x = (sx - game_rect.left) // cell_size
        y = (sy - game_rect.top) // cell_size
        if (0 <= x < self.game_config.width) and (0 <= y < self.game_config.height):
            return self.toggle((x, y))

        return ClickEffect.OUTSIDE_GAME
