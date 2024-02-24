from pathlib import Path
import typing
import enum
import pygame
from pygame import Rect

from .constants import *
from .game_types import *
from .deterministic_random import DeterministicRandom
from .colour import Colour
from .game_config import GameConfig



class NotEnoughImageFilesError(Exception):
    pass

class LockType(enum.Enum):
    UNLOCK = enum.auto()
    LOCK_GOOD = enum.auto()
    LOCK_BAD = enum.auto()

class Images:
    def __init__(self, img_dir_path: Path) -> None:
        self.all_images: typing.List[Image] = []
        for file_name in get_all_images(img_dir_path):
            self.all_images.append(Image(file_name))

        if len(self.all_images) < MAX_NUM_VALUES:
            raise NotEnoughImageFilesError(
                f"Only {len(self.all_images)} found, need at least {MAX_NUM_VALUES}")

        self.value_images: typing.List[Image] = []
        self.backgrounds: typing.List[Background] = []
        self.lock_image = Image(img_dir_path / "bone.png")
        self.bad_lock_image = Image(img_dir_path / "badbone.png")
        self.icon_path = img_dir_path / "storm.png"
        self.game_config = GameConfig(1, 0)

    def get_icon(self) -> SurfaceType:
        return pygame.image.load(self.icon_path)

    def prepare(self, game_config: GameConfig) -> None:
        self.game_config = game_config
        assert self.game_config.num_values <= MAX_NUM_VALUES
        rng = DeterministicRandom(self.game_config.level_id, self.game_config.seed)

        self.value_images.clear()
        img_choose_from = self.all_images[:]
        while (len(self.value_images) < self.game_config.num_values) and (len(img_choose_from) != 0):
            self.value_images.append(img_choose_from.pop(rng.randrange(0, len(img_choose_from))))

        self.backgrounds.clear()
        colour_choose_from = list(range(1, MAX_NUM_VALUES))
        while (len(self.backgrounds) < self.game_config.num_values) and (len(colour_choose_from) != 0):
            val = colour_choose_from.pop(rng.randrange(0, len(colour_choose_from)))
            colour = Colour((val & 2) * 127, (val & 4) * 63, (val & 1) * 255).brighten(200)
            x = rng.randrange(0, self.game_config.width)
            y = rng.randrange(0, self.game_config.height)
            self.backgrounds.append(Background(colour, (x, y), (self.game_config.width, self.game_config.height)))

    def draw(self, value: int,
             game_area: SurfaceType, cell_rect: RectType,
             lock_type: LockType = LockType.UNLOCK, brightness: int = 0) -> None:

        # Draw part of background
        self.backgrounds[value].draw(game_area, cell_rect)

        # Draw highlighting
        pygame.draw.rect(game_area, (brightness, brightness, 0),
                         cell_rect, max(1, cell_rect.width // 40))
        # Draw cell
        cell_area = game_area.subsurface(cell_rect)
        self.value_images[value].draw(cell_area)

        # Draw lock icon
        if lock_type == LockType.LOCK_GOOD:
            self.lock_image.draw(cell_area)
        elif lock_type == LockType.LOCK_BAD:
            self.bad_lock_image.draw(cell_area)

    def get_num_values(self) -> int:
        return self.game_config.num_values

class Background:
    def __init__(self, colour: Colour, cxy: GridXY, wh: GridXY) -> None:
        self.colour = colour
        self.scale_from: SurfaceType = pygame.Surface(wh)
        (w, h) = wh
        (cx, cy) = cxy
        size = max(w, h)
        for y in range(h):
            for x in range(w):
                distance = abs(x - cx) + abs(y - cy)
                self.scale_from.set_at((x, y), self.colour.darken((distance * 200) // size).get_rgb())

        self.resized = self.scale_from.copy()

    def draw(self, game_area: SurfaceType, cell_rect: RectType, special_flags: int = 0) -> None:
        size = game_area.get_rect().size
        if size != self.resized.get_rect().size:
            self.resized = pygame.transform.smoothscale(self.scale_from, size)

        game_area.blit(source=self.resized,
                       dest=cell_rect,
                       area=cell_rect,
                       special_flags=special_flags)

class Image:
    def __init__(self, path: Path) -> None:
        self.path = path

        original = pygame.image.load(str(path))
        original_rect = original.get_rect()

        size = max(original_rect.width, original_rect.height)
        original_rect.center = (size // 2, size // 2)

        self.scale_from: SurfaceType 
        self.scale_from = pygame.Surface((size, size), flags=pygame.SRCALPHA)
        self.scale_from.blit(original, original_rect.topleft)
        self.resized: SurfaceType = self.scale_from.copy()

    def draw(self, target: SurfaceType, special_flags: int = 0) -> None:
        if self.resized.get_rect().size != target.get_rect().size:
            self.resized = pygame.transform.smoothscale(self.scale_from, target.get_rect().size)
        target.blit(self.resized, (0, 0), special_flags=special_flags)

def get_all_images(img_dir_path: Path) -> typing.List[Path]:
    file_names: typing.List[Path] = []
    for file_name in sorted((img_dir_path / "dogs").iterdir()):
        if file_name.suffix.lower() in (".png", ".jpeg", ".jpg"):
            file_names.append(file_name)
    return file_names
