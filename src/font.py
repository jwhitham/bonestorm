from pathlib import Path
import pygame
import typing
from pygame import Rect

from .game_types import *
from .constants import *
from .colour import Colour

class Font:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.font_file = path / "DejaVuSans.ttf"
        self.font_cache: typing.Dict[typing.Any, pygame.font.Font] = {}
        self.size_cache: typing.Dict[typing.Any, ScreenXY] = {}
        self.draw_cache: typing.Dict[typing.Any, SurfaceType] = {}

    def get_font(self, font_size: int) -> pygame.font.Font:
        font = self.font_cache.get(font_size, None)
        if font is None:
            if len(self.font_cache) >= MAX_CACHE_SIZE:
                self.font_cache.clear()
            self.font_cache[font_size] = font = pygame.font.Font(str(self.font_file), font_size)
        return font

    def get_size(self, text: str, font_size: int) -> ScreenXY:
        key = (text, font_size)
        size = self.size_cache.get(key, None)
        if size is None:
            font = self.get_font(font_size)
            if len(self.size_cache) >= MAX_CACHE_SIZE:
                self.size_cache.clear()
            self.size_cache[key] = size = font.size(text)
        return size

    def draw(self, text_area: SurfaceType, text: str, colour: "Colour",
                horizontal_align = 0,
                vertical_align = 0) -> None:

        # Cached?
        text_rect = text_area.get_rect()
        key = (text, text_rect.size, colour, horizontal_align, vertical_align)
        draw_area = self.draw_cache.get(key, None)
        if draw_area is not None:
            text_area.blit(draw_area, (0, 0))
            return

        # Not cached - start from the beginning
        draw_area = pygame.Surface(text_rect.size, pygame.SRCALPHA)

        # We will now fit the text to the available space, finding the largest size that fits
        low_size = 4
        high_size = 100
        while low_size < (high_size - 1):
            size = (low_size + high_size) // 2
            try:
                WordLocations(text=text, container_rect=text_rect,
                              size=size, horizontal_align=horizontal_align,
                              vertical_align=vertical_align, font=self)
                low_size = size
            except TooBigError:
                high_size = size

        # Determine the word locations again for the given size
        size = low_size
        try:
            WordLocations(text=text, container_rect=text_rect,
                          size=size, horizontal_align=horizontal_align,
                          vertical_align=vertical_align,
                          font=self).render(draw_area, self.get_font(size), colour.get_rgb())
        except TooBigError:
            # The text cannot be rendered at all
            pass

        # Cache management
        if len(self.draw_cache) >= MAX_CACHE_SIZE:
            self.draw_cache.clear()
        self.draw_cache[key] = draw_area

        # Draw
        text_area.blit(draw_area, (0, 0))

class TooBigError(Exception):
    pass

class WordLocations:
    def __init__(self, text: str, container_rect: RectType, size: int,
                horizontal_align: int, vertical_align: int, font: Font) -> None:
        # Here is the available space for the text
        self.container_rect = container_rect

        # Here are the locations of the words
        self.word_loc: typing.List[typing.Tuple[RectType, str]] = []

        # Plan where the words would be, assuming this size, and align left and align top.
        max_width = 0
        max_height = 0
        row_width: typing.Dict[int, int] = {}
        y = 0
        for line in text.split("\n"):
            words = line.split()
            x = 0
            line_height = 0
            for word in words:
                (w, h) = font.get_size(" " + word, size)
                if (w + x) > self.container_rect.width:
                    # Wrap to next line
                    y += line_height 
                    x = 0
                    self.word_loc.append((Rect(x, y, w, h), word))
                    x += w
                    line_height = h
                else:
                    # Add to current line
                    self.word_loc.append((Rect(x, y, w, h), word))
                    x += w
                    line_height = max(h, line_height)

                row_width[y] = x
                max_width = max(x, max_width)
                max_height = y + line_height
                if max_height > self.container_rect.height:
                    # Ran out of space
                    raise TooBigError()

            # Allow for blank lines
            if line_height == 0:
                (w, h) = font.get_size("X", size)
                line_height = h
                max_height = y + line_height

            # Always go to a new line
            y += line_height
            x = 0

        # Here is the container for the text - the width spans the whole container
        # because horizontal alignment requires modifying each line separately.
        self.text_rect = Rect(0, 0, self.container_rect.width, max_height)
        self.text_rect.topleft = self.container_rect.topleft

        # Vertical alignment is set by moving the whole container
        if vertical_align == 0:
            self.text_rect.centery = self.container_rect.centery
        elif vertical_align > 0:
            self.text_rect.bottom = self.container_rect.bottom

        # Horizontal alignment is set row-by-row.
        # Move words according to alignment
        for i in range(len(self.word_loc)):
            (r, word) = self.word_loc[i]
            if horizontal_align == 0:
                r.left += (self.container_rect.width - row_width[r.top]) // 2
            elif horizontal_align > 0:
                r.left += (self.container_rect.width - row_width[r.top])
            self.word_loc[i] = (r, word)
        
    def render(self, draw_area: SurfaceType, f: pygame.font.Font, colour: ColourType) -> None:
        for (r, word) in self.word_loc:
            r.left += self.text_rect.left
            r.top += self.text_rect.top
            draw_area.blit(f.render(word, True, colour), r.topleft)
