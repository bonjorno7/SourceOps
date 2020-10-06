import bpy
from pathlib import Path


def resolve(path):
    if path:
        return str(Path(bpy.path.abspath(path)).resolve())
    else:
        return ''


def update_game(self, context):
    self['game'] = resolve(self.game)
    game = Path(self.game)

    if game.joinpath('gameinfo.txt').is_file():
        self['bin'] = str(game.parent.joinpath('bin'))
        self['modelsrc'] = str(game.joinpath('modelsrc'))
        self['models'] = str(game.joinpath('models'))
        self['maps'] = str(game.joinpath('maps'))


def update_bin(self, context):
    self['bin'] = resolve(self.bin)


def update_modelsrc(self, context):
    self['modelsrc'] = resolve(self.modelsrc)


def update_models(self, context):
    self['models'] = resolve(self.models)


def update_maps(self, context):
    self['maps'] = resolve(self.maps)


def verify(game):
    gameinfo = Path(game.game).joinpath('gameinfo.txt')
    studiomdl = Path(game.bin).joinpath('studiomdl.exe')
    return gameinfo.is_file() and studiomdl.is_file()
