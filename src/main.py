import typing
import pygame
import os
import argparse
import sys
from pathlib import Path

from .constants import *
from .game_types import *
from .images import Images
from .font import Font
from .game_database import GameDatabase
from .state import TitleState, BaseState
from .test_speedrun import test_speedrun
from .variant import Variant


def pyinstaller_main(internal_flag: bool) -> int:
    root_path = Path(sys.prefix)
    return common_main(
            root_path=root_path,
            variant_path=(root_path / "variants" / "home.json")
                            if internal_flag else None)

def python_main(argv: typing.List[str]) -> int:
    parser = argparse.ArgumentParser(prog='Bone Storm', description='Game')
    parser.add_argument("--test-speedrun", type=int, metavar="frames_per_move")
    parser.add_argument("--database", type=str, metavar="filename")
    parser.add_argument("--upgrade-database", action="store_true")
    parser.add_argument("--variant", type=str, metavar="filename")
    args = parser.parse_args(argv)

    if args.test_speedrun:
        return test_speedrun(int(args.test_speedrun))

    root_path = Path(__file__).parent.parent.absolute()
    return common_main(root_path,
            database_path=Path(args.database) if args.database else None,
            upgrade_database_only=bool(args.upgrade_database),
            variant_path=Path(args.variant) if args.variant else None)

def is_android() -> bool:
    return hasattr(sys, 'getandroidapilevel')

def common_main(root_path: Path,
                database_path: typing.Optional[Path] = None,
                upgrade_database_only: bool = False,
                variant_path: typing.Optional[Path] = None) -> int:

    pygame.init()
    pygame.font.init()

    if not database_path:
        database_dir_path = root_path
        if is_android():
            # Database is with the app storage
            print("Bone Storm for Android")
            try:
                from android.storage import app_storage_path # type: ignore
                database_dir_path = Path(app_storage_path())
            except Exception:
                pass
        else:
            # Database in HOME (preferred) or APPDATA
            for env_name in ["APPDATA", "HOME"]:
                home = os.getenv(env_name)
                if (home is not None) and Path(home).is_dir():
                    database_dir_path = Path(home)

        database_path = database_dir_path / ".bonestorm"

    game_database = GameDatabase(database_path)

    if upgrade_database_only:
        return 0

    if not variant_path:
        if is_android():
            variant_path = root_path / "variants" / "android.json"
        else:
            variant_path = root_path / "variants" / "desktop.json"

    images = Images(root_path / "img")
    font = Font(root_path / "font")
    variant = Variant(variant_path)

    clock = pygame.time.Clock()
    pygame.display.set_caption("Bone Storm")
    pygame.display.set_icon(images.get_icon())

    try:
        return main_loop(clock=clock, images=images, font=font,
                         variant=variant, game_database=game_database)
    finally:
        pygame.quit()

def main_loop(clock: pygame.time.Clock,
                images: Images, font: Font,
                variant: Variant,
                game_database: GameDatabase) -> int:

    # Launch the game
    has_input_focus = False
    mouse_pos = (-1, -1)
    state: BaseState = TitleState(variant, game_database)
    if variant.constants.FORCE_WIDTH and variant.constants.FORCE_HEIGHT:
        size = (variant.constants.FORCE_WIDTH, variant.constants.FORCE_HEIGHT)
        flags = 0
    else:
        size = game_database.get_window_size()
        flags = pygame.RESIZABLE
    screen_area = pygame.display.set_mode(size=size, flags=flags)
    screen_area.fill(variant.palette.WINDOW_BG)
    run_time = 0

    while not state.quit_flag:
        run_time += clock.tick(FRAME_RATE_HZ)

        if has_input_focus:
            # When running, advance by at least one frame
            run_time -= ONE_FRAME_TIME_MS
            state = state.update()

            # Update by more frames if time was skipped (up to MAX_SKIP_TIME_MS)
            run_time = min(MAX_SKIP_TIME_MS, run_time)
            while run_time >= ONE_FRAME_TIME_MS:
                run_time -= ONE_FRAME_TIME_MS
                state = state.update()
        else:
            # When paused, don't track frame skipping
            run_time = 0

        if ((screen_area.get_rect().height < 100)
        or (screen_area.get_rect().width < 100)):
            # Screen is too small
            screen_area.fill(variant.palette.WINDOW_BG)
        else:
            state.draw(screen_area, mouse_pos, images, font)

        pygame.display.flip()

        # Process events
        if has_input_focus:
            e = pygame.event.poll()
        else:
            e = pygame.event.wait()

        while e.type != pygame.NOEVENT:
            if e.type == pygame.QUIT:
                return 0

            elif e.type == pygame.VIDEORESIZE:
                game_database.set_window_size(screen_area.get_rect().size)

            elif e.type == pygame.ACTIVEEVENT:
                if e.state == pygame.APPINPUTFOCUS:
                    has_input_focus = (e.gain != 0)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                state = state.click(e.pos)

            elif e.type == pygame.MOUSEMOTION and variant.constants.DESKTOP:
                mouse_pos = e.pos

            elif e.type == pygame.MOUSEBUTTONUP:
                pass

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F10:
                    return 0
                if e.key == pygame.K_ESCAPE:
                    state = state.cancel()

            e = pygame.event.poll()

    return 0
