import bpy
from pathlib import Path
from . import common


def update_game(self, context):
    game = common.resolve_path(self.game)
    self['game'] = str(game)

    if game.joinpath('gameinfo.txt').is_file():
        self['bin'] = str(game.parent.joinpath('bin'))
        self['modelsrc'] = str(game.joinpath('modelsrc'))
        self['models'] = str(game.joinpath('models'))
        self['maps'] = str(game.joinpath('maps'))


def update_bin(self, context):
    self['bin'] = str(common.resolve_path(self.bin))


def update_modelsrc(self, context):
    self['modelsrc'] = str(common.resolve_path(self.modelsrc))


def update_models(self, context):
    self['models'] = str(common.resolve_path(self.models))


def update_maps(self, context):
    self['maps'] = str(common.resolve_path(self.maps))


def verify(game):
    gameinfo = Path(game.game).joinpath('gameinfo.txt')
    studiomdl = Path(game.bin).joinpath('studiomdl.exe')
    return gameinfo.is_file() and studiomdl.is_file()
