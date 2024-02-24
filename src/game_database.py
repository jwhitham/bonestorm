from pathlib import Path
import enum
import sqlite3
import typing
import os
import time

from .game_types import *

class UpdateEffect(enum.Enum):
    COMPLETED_FIRST_TIME = enum.auto()
    NO_IMPROVEMENT = enum.auto()
    BETTER_SCORE = enum.auto()
    BETTER_TIME_AND_SCORE = enum.auto()
    BETTER_TIME = enum.auto()
    OUT_OF_TIME = enum.auto()

class PlayInfo:
    def __init__(self,
            last_score: typing.Optional[int],
            best_counter: typing.Optional[int],
            played: int,
            completed: int) -> None:
        self.last_score = last_score
        self.best_counter = best_counter
        self.played = played
        self.completed = completed

    def copy(self) -> "PlayInfo":
        return PlayInfo(
            last_score=self.last_score,
            best_counter=self.best_counter,
            played=self.played,
            completed=self.completed)

class DatabaseError(Exception):
    pass

class GameDatabase:
    def __init__(self, file_name: Path) -> None:
        self.file_name = file_name
        init = not self.file_name.is_file()
        try:
            self.db = sqlite3.connect(self.file_name, isolation_level=None)
        except Exception as e:
            raise DatabaseError(f"Database connection error: {self.file_name}: {e}")

        if init:
            self.init_database()

        self.upgrade_database()

    def init_database(self) -> None:
        # Always create a version 1 schema
        c = self.db.cursor()
        c.execute("BEGIN TRANSACTION")
        try:
            c.execute("""
CREATE TABLE version (dbv INTEGER NOT NULL)""")
            c.execute("""
INSERT INTO version (dbv) VALUES (1)""") # <-- always version 1
            c.execute("""
CREATE TABLE window_size (width INTEGER NOT NULL, height INTEGER NOT NULL)""")
            c.execute("""
INSERT INTO window_size (width, height) VALUES (1000, 500)""")
            c.execute("""
CREATE TABLE score
       (level_id INTEGER NOT NULL,
        last_score INTEGER,
        best_counter INTEGER,
        played INTEGER NOT NULL,
        completed INTEGER NOT NULL,
        last_played REAL NOT NULL,
        PRIMARY KEY (level_id))""")
        finally:
            c.execute("COMMIT TRANSACTION")
            self.db.commit()

    def upgrade_database(self) -> None:
        # Upgrade database schema from any old version to the current version
        c = self.db.cursor()
        c.execute("BEGIN TRANSACTION")
        try:
            c.execute("""SELECT dbv FROM version""")
            f = c.fetchone()
            if (f is None) or (not isinstance(f[0], int)):
                raise DatabaseError(f"Database does not have a valid version table: {self.file_name}")
            old_version = f[0]
            if (old_version < 1) or (old_version > 2):
                raise DatabaseError(f"Database version {old_version} is unknown: {self.file_name}")

            if old_version == 1:
                # Upgrade from version 1 to 2
                c.execute("""ALTER TABLE score ADD COLUMN seed INTEGER""")
                c.execute("""UPDATE version SET dbv = 2""")

        finally:
            c.execute("COMMIT TRANSACTION")
            self.db.commit()

    def get_window_size(self) -> ScreenXY:
        c = self.db.cursor()
        c.execute("""SELECT width, height FROM window_size""")
        f = c.fetchone()
        assert f is not None
        assert None not in f
        return (int(f[0]), int(f[1]))

    def set_window_size(self, wh: ScreenXY) -> None:
        c = self.db.cursor()
        c.execute("""UPDATE window_size SET width = ?, height = ?""", wh)
        self.db.commit()

    def get_most_recent_level_played(self) -> int:
        c = self.db.cursor()
        c.execute("""SELECT level_id FROM score WHERE played > 0 ORDER BY last_played DESC LIMIT 1""")
        f = c.fetchone()
        if f is None:
            return 1
        else:
            return f[0]

    def get_maximum_level_completed(self) -> int:
        c = self.db.cursor()
        c.execute("""SELECT level_id FROM score WHERE completed > 0 ORDER BY level_id DESC LIMIT 1""")
        f = c.fetchone()
        if f is None:
            return 0
        else:
            return f[0]

    def get_score_and_time_up_to_and_including_level(self, level_id: int) -> typing.Tuple[int, int]:
        c = self.db.cursor()
        c.execute("""SELECT SUM(last_score), SUM(best_counter) FROM score WHERE level_id <= ?""",
                (level_id, ))
        f = c.fetchone()
        if (f is None) or (None in f):
            return (0, 0)
        else:
            return (f[0], f[1])

    def set_seed_for_level(self, level_id: int, seed: int) -> None:
        c = self.db.cursor()
        c.execute("BEGIN TRANSACTION")
        try:
            c.execute("""UPDATE score SET seed = ? WHERE level_id = ?""", (seed, level_id))
        finally:
            c.execute("COMMIT TRANSACTION")
            self.db.commit()

    def get_seed_for_level(self, level_id: int) -> int:
        c = self.db.cursor()
        c.execute("""SELECT seed FROM score WHERE level_id = ?""", (level_id, ))
        f = c.fetchone()
        if (f is None) or (None in f):
            return 0
        else:
            return f[0]

    def get_play_info_for_level(self, level_id: int) -> PlayInfo:
        return self.__get_play_info_for_level(self.db.cursor(), level_id)

    def __get_play_info_for_level(self, c: sqlite3.Cursor, level_id: int) -> PlayInfo:
        c.execute("""SELECT last_score, best_counter, played, completed FROM score WHERE level_id = ?""",
                (level_id, ))
        f = c.fetchone()
        if f is None:
            return PlayInfo(last_score=None, best_counter=None, played=0, completed=0)

        return PlayInfo(last_score=f[0],
                        best_counter=f[1],
                        played=f[2] if (f[2] is not None) else 0,
                        completed=f[3] if (f[3] is not None) else 0)

    def __set_play_info_for_level(self, c: sqlite3.Cursor, level_id: int, new_result: PlayInfo) -> None:
        # Check table for an existing entry for this level
        c.execute("""SELECT played FROM score WHERE level_id = ?""", (level_id, ))
        f = c.fetchone()
        if (f is None) or (f[0] is None):
            # No table row for this level_id - create it
            c.execute("""INSERT INTO score
                    (level_id, last_played, played, completed)
                    VALUES (?, 0, 0, 0)""", (level_id, ))

        # Update existing entry
        c.execute("""UPDATE score SET played = ?, completed = ?, last_played = ?
                        WHERE level_id = ?""",
                            (new_result.played, new_result.completed, time.time(), level_id))
        if new_result.best_counter is not None:
            c.execute("""UPDATE score SET best_counter = ? WHERE level_id = ?""",
                                (new_result.best_counter, level_id))
        if new_result.last_score is not None:
            c.execute("""UPDATE score SET last_score = ? WHERE level_id = ?""",
                                (new_result.last_score, level_id))

    def failed_attempt_at_level(self, level_id: int) -> UpdateEffect:
        c = self.db.cursor()
        c.execute("BEGIN TRANSACTION")
        try:
            previous_result = self.__get_play_info_for_level(c, level_id)
            new_result = previous_result.copy()
            new_result.played += 1
            self.__set_play_info_for_level(c, level_id, new_result)
            return UpdateEffect.NO_IMPROVEMENT
        finally:
            c.execute("COMMIT TRANSACTION")
            self.db.commit()

    def successful_attempt_at_level(self, level_id: int, score: int, counter: int) -> UpdateEffect:
        c = self.db.cursor()
        c.execute("BEGIN TRANSACTION")
        try:
            previous_result = self.__get_play_info_for_level(c, level_id)
            new_result = previous_result.copy()
            new_result.played += 1
            new_result.completed += 1
            better_score = False
            better_time = False

            if (previous_result.last_score is None) or (score > previous_result.last_score):
                new_result.last_score = score       # Better score
                better_score = True

            if (previous_result.best_counter is None) or (counter < previous_result.best_counter):
                new_result.best_counter = counter   # Better time
                better_time = True

            self.__set_play_info_for_level(c, level_id, new_result)

            if new_result.completed == 1:
                return UpdateEffect.COMPLETED_FIRST_TIME
            elif better_score and better_time:
                return UpdateEffect.BETTER_TIME_AND_SCORE
            elif better_time:
                return UpdateEffect.BETTER_TIME
            elif better_score:
                return UpdateEffect.BETTER_SCORE
            else:
                return UpdateEffect.NO_IMPROVEMENT
        finally:
            c.execute("COMMIT TRANSACTION")
            self.db.commit()
