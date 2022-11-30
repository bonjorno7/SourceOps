import os
from pathlib import Path
from ..utils.common import resolve

def update_game(self, context):
    self['game'] = resolve(self.game)
    game = Path(self.game)

    if game.joinpath('gameinfo.txt').is_file():
        bin = game.parent.joinpath('bin')

        # If we're not on the old-style pattern bin/<something> layout, check for platform subdirs
        actualbin = None
        if not bin.joinpath('studiomdl.exe').is_file() and not bin.joinpath('studiomdl').is_file():
            def check_subdir(subdirs, studiomdl):
                for subdir in subdirs:
                    path = bin.joinpath(subdir)
                    if path.is_dir() and path.joinpath(studiomdl).is_file():
                        return path
                return None

            # For linux, prefer the native binaries (if possible)
            if os.name == 'posix':
                actualbin = check_subdir(['linux32', 'linux64'], 'studiomdl')
            # Resolve windows paths
            if actualbin is None:
                actualbin = check_subdir(['win32', 'win64'], 'studiomdl.exe')

        if actualbin is not None:
            bin = actualbin

        self['bin'] = str(bin)
        self['modelsrc'] = str(game.joinpath('modelsrc'))
        self['models'] = str(game.joinpath('models'))
        self['mapsrc'] = str(game.joinpath('mapsrc'))


def update_bin(self, context):
    self['bin'] = resolve(self.bin)


def update_modelsrc(self, context):
    self['modelsrc'] = resolve(self.modelsrc)


def update_models(self, context):
    self['models'] = resolve(self.models)


def update_mapsrc(self, context):
    self['mapsrc'] = resolve(self.mapsrc)


def verify(game):
    gameinfo = Path(game.game).joinpath('gameinfo.txt')
    return gameinfo.is_file() and get_studiomdl_path(game).is_file()

def get_studiomdl_path(game):
    if os.name == 'posix' and (game.bin.endswith('linux32') or game.bin.endswith('linux64')):
        path = Path(game.bin).joinpath('studiomdl')
        if path.is_file():
            return path
    return Path(game.bin).joinpath('studiomdl.exe')

