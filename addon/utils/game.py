from pathlib import Path
from ..utils.common import resolve


def update_game(self, context):
    self['game'] = resolve(self.game)
    game = Path(self.game)

    if game.joinpath('gameinfo.txt').is_file():
        bin = game.parent.joinpath('bin')

        if not bin.joinpath('studiomdl.exe').is_file():
            for path in bin.iterdir():
                if path.is_dir() and path.joinpath('studiomdl.exe').is_file():
                    bin = path
                    break

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
    studiomdl = Path(game.bin).joinpath('studiomdl.exe')
    return gameinfo.is_file() and studiomdl.is_file()
