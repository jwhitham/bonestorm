
import collections
import typing

from .constants import *
from .game_types import *
from .deterministic_random import DeterministicRandom
from .grid import Grid
from .game_config import GameConfig


class BasePattern:
    def __init__(self) -> None:
        self.plan: typing.Dict[int, typing.List[GridXY]] = collections.defaultdict(lambda: [])
        self.sequence = 0
        self.change_point_for_xy: typing.Dict[GridXY, int] = {}
        self.plan_duration = 0

    def make_plan(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        raise NotImplementedError()

    def analyse_plan(self) -> None:
        for time in sorted(self.plan):
            change_point = time + PLAN_LEADIN_FRAMES
            self.plan_duration = max(self.plan_duration, time + 1)
            for xy in self.plan[time]:
                assert xy not in self.change_point_for_xy, ("A cell may not change twice during a plan")
                self.change_point_for_xy[xy] = change_point

    def is_leadin(self) -> bool:
        return self.sequence < PLAN_LEADIN_FRAMES

    def is_leadout(self) -> bool:
        return self.sequence >= (PLAN_LEADIN_FRAMES + self.plan_duration)

    def is_done(self) -> bool:
        return self.sequence >= (PLAN_LEADIN_FRAMES + PLAN_LEADOUT_FRAMES + self.plan_duration)

    def update(self, grid: Grid) -> None:
        self.sequence += 1
        for xy in self.plan.get(self.sequence - PLAN_LEADIN_FRAMES, []):
            grid.update(xy, 1)

    def get_brightness(self, xy: GridXY) -> int:
        change_point = self.change_point_for_xy.get(xy, -1)
        if change_point < 0:
            return 0 # xy never changes in this plan

        change_delta = change_point - self.sequence
        if change_delta > 0:
            # Change is in the future
            return max(220 - abs(change_delta * 5), 0)
        elif change_delta < 0:
            # Change is in the past
            return max(220 - abs(change_delta * 25), 0)
        else:
            # Change is now
            return 255

class HorizontalWipePattern(BasePattern):
    def make_plan(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        # Determine the direction of the wipe
        if rng.randrange(0, 2) == 0:
            dx = -1
            x = game_config.width - 1
        else:
            dx = 1
            x = 0

        # Plan the changes
        for i in range(game_config.width):
            self.plan[i * UPDATE_PERIOD_FRAMES] = [(x, y) for y in range(game_config.height)]
            x += dx

class VerticalWipePattern(BasePattern):
    def make_plan(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        # Determine the direction of the wipe
        if rng.randrange(0, 2) == 0:
            dy = -1
            y = game_config.height - 1
        else:
            dy = 1
            y = 0

        # Plan the changes
        for i in range(game_config.height):
            self.plan[i * UPDATE_PERIOD_FRAMES] = [(x, y) for x in range(game_config.width)]
            y += dy


class GrowPattern(BasePattern):
    def make_plan(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        cx = rng.randrange(0, game_config.width)
        cy = rng.randrange(0, game_config.height)

        done: typing.Set[GridXY] = set()
        i = 0
        while len(done) != (game_config.width * game_config.height):
            for y in range(game_config.height):
                for x in range(game_config.width):
                    distance = abs(x - cx) + abs(y - cy)
                    if distance == i:
                        assert (x, y) not in done
                        self.plan[i * UPDATE_PERIOD_FRAMES].append((x, y))
                        done.add((x, y))
            i += 1
            assert i < RUNAWAY_LIMIT

class ShrinkPattern(GrowPattern):
    def make_plan(self, rng: DeterministicRandom, game_config: GameConfig) -> None:
        GrowPattern.make_plan(self, rng, game_config)

        old_plan = dict(self.plan)
        all_keys = sorted(old_plan)
        end_time = max(all_keys)
        self.plan.clear()

        for time in all_keys:
            self.plan[end_time - time] = old_plan[time]

PATTERNS = [GrowPattern, ShrinkPattern,
            VerticalWipePattern, HorizontalWipePattern]

