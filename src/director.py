import typing
import pygame

from .constants import *
from .game_types import *
from .images import Images, LockType
from .colour import Colour
from .grid import Grid, ClickEffect
from .deterministic_random import DeterministicRandom
from .patterns import BasePattern, PATTERNS
from .game_config import GameConfig

class Director:
    def __init__(self, game_config: GameConfig) -> None:
        self.game_config = game_config
        self.rng = DeterministicRandom(self.game_config.level_id, self.game_config.seed)
        self.grid = Grid(self.rng, self.game_config)
        self.patterns: typing.List[BasePattern] = []
        self.plan_sequence = PLAN_PERIOD_FRAMES - 1
        self.flash_sequence = 0

    def update(self) -> None:
        self.plan_sequence += 1
        i = 0
        while i < len(self.patterns):
            pattern = self.patterns[i]
            pattern.update(self.grid)
            if pattern.is_done():
                self.patterns.pop(i)
            else:
                i += 1

        if self.plan_sequence >= PLAN_PERIOD_FRAMES:
            self.plan_sequence -= PLAN_PERIOD_FRAMES
            pattern_class = PATTERNS[self.rng.randrange(0, len(PATTERNS))]
            pattern = pattern_class()
            pattern.make_plan(self.rng, self.game_config)
            pattern.analyse_plan()
            self.patterns.append(pattern)

        self.flash_sequence += 1
        if self.flash_sequence >= FLASH_INTERVAL_FRAMES:
            self.flash_sequence = 0

    def draw(self, game_area: SurfaceType, images: Images) -> None:
        game_rect = game_area.get_rect()
        largest_lock_group: typing.Optional[int] = None
        if self.flash_sequence < FLASH_DURATION_FRAMES:
            largest_lock_group = self.grid.get_largest_lock_group()

        for y in range(self.game_config.height):
            for x in range(self.game_config.width):
                brightness = 0
                for pattern in self.patterns:
                    brightness = max(brightness, pattern.get_brightness((x, y)))

                cell = self.grid.get_cell((x, y))
                assert cell is not None

                lock_type = LockType.UNLOCK 
                if cell.is_locked():
                    if ((largest_lock_group is not None)
                    and (cell.get_lock_group() != largest_lock_group)):
                        lock_type = LockType.LOCK_BAD
                    else:
                        lock_type = LockType.LOCK_GOOD

                cell_rect = self.grid.get_cell_rect(game_rect, (x, y))
                images.draw(value=cell.get_value(),
                            lock_type=lock_type,
                            brightness=brightness,
                            game_area=game_area,
                            cell_rect=cell_rect)

    def is_complete(self) -> bool:
        return self.grid.is_complete()

    def click(self, game_rect: RectType, xy: ScreenXY) -> ClickEffect:
        return self.grid.click(game_rect, xy)

    def speedrun(self, lock_group: int, frames_per_move: int, counter_limit: int) -> typing.Optional[int]:
        # Return the minimum number of moves to complete the game, using a simple algorithm
        cx = self.game_config.width // 2
        cy = self.game_config.height // 2
        counter = 0
        max_distance = self.game_config.width + self.game_config.height
        while (not self.grid.is_complete()) and (counter < counter_limit):
            # Find the best place to lock - nearest the current place
            fallback_distance = best_distance = max_distance
            best_xy: typing.Optional[GridXY] = None
            fallback_xy: GridXY = (cx, cy)
            for y in range(self.game_config.height):
                for x in range(self.game_config.width):
                    cell = self.grid.get_cell((x, y))
                    assert cell is not None
                    dist = abs(x - cx) + abs(y - cy)
                    if not cell.is_locked():
                        if cell.get_value() == lock_group:
                            # This is a correct cell to lock
                            if dist < best_distance:
                                best_distance = dist
                                best_xy = (x, y)
                        else:
                            # This is not a correct cell yet but maybe it will be
                            if dist < fallback_distance:
                                fallback_distance = dist
                                fallback_xy = (x, y)

            if (counter % frames_per_move) == 0:
                # Move towards a lockable place
                if best_xy is not None:
                    (x, y) = best_xy
                else:
                    (x, y) = fallback_xy

                if x < cx:
                    cx -= 1
                elif x > cx:
                    cx += 1
                elif y > cy:
                    cy += 1
                elif y < cy:
                    cy -= 1
                elif best_xy is not None:
                    # We're already in a lockable place, so lock now
                    assert best_xy == (cx, cy)
                    ce = self.grid.toggle(best_xy)
                    cell = self.grid.get_cell(best_xy)
                    assert ce in (ClickEffect.LOCK_GOOD, ClickEffect.LOCK_NEUTRAL)
                    assert cell is not None
                    assert cell.get_lock_group() == lock_group
                    no_progress = 0

            # Update the grid
            counter += 1
            self.update()

        if self.grid.is_complete():
            # Strictly, the game was complete before the last update, so subtract 1
            return counter - 1

        return None
