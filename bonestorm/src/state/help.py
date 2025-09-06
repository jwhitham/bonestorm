import typing

from ..constants import *
from ..game_types import *
from ..game_database import GameDatabase
from ..variant import Variant

from .base import BaseState
from .intermission import IntermissionState


class HelpState(IntermissionState):
    def __init__(self, variant: Variant, game_database: GameDatabase) -> None:
        IntermissionState.__init__(self, variant, game_database)

        self.headline = "How to Play"

        self.info_messages.append("Select matching tiles as quickly as you can!")
        self.info_messages.append("")
        self.info_messages.append("""
                    To complete each level, select matching tiles. 
                    When a tile is selected, it's marked with a bone.
                    The level is complete when all of the tiles match and are marked with a bone.
        """.replace("\n", " "))
        self.info_messages.append("""
                    Tiles that are not marked will change periodically.
                    The sequence of changes is predictable and by learning to
                    recognise the sequence in each level, you can match the tiles faster,
                    unlock more levels and get a higher score.
        """.replace("\n", " "))

        self.info_area_horizontal_align = -1
        self.buttons.append(("Go to Title Screen", self.return_to_title, 0))
