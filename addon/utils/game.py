from pathlib import Path
from ..utils.common import resolve


def update_game(self, context):
    self['game'] = resolve(self.game)
    game = Path(self.game)

    if game.joinpath('gameinfo.txt').is_file():
        bin32 = game.parent.joinpath('bin')
        bin64 = bin32.joinpath('win64')
        
        if bin64.is_dir() and bin64.joinpath('studiomdl.exe').is_file():
            bin = bin64
        elif bin32.is_dir() and bin32.joinpath('studiomdl.exe').is_file():
            bin = bin32
        else:
            for path in bin32.iterdir():
                if path.is_dir() and path.joinpath('studiomdl.exe').is_file():
                    bin = path
                    break

        quickmdl     = bin.joinpath('quickmdl.exe')
        studiomdl    = bin.joinpath('studiomdl.exe')

        hlmv         = bin.joinpath('hlmv.exe')
        hlmvplusplus = bin.joinpath('hlmvplusplus.exe')

        self['bin']       = str(bin)
        self['studiomdl'] = str(quickmdl if quickmdl.is_file() else studiomdl)
        self['hlmv']      = str(hlmvplusplus if hlmvplusplus.is_file() else hlmv)

        self['modelsrc'] = str(game.joinpath('modelsrc'))
        self['models']   = str(game.joinpath('models'))
        self['mapsrc']   = str(game.joinpath('mapsrc'))


def update_bin(self, context):
    self['bin'] = resolve(self.bin)

def update_studiomdl(self, context):
    self['studiomdl'] = resolve(self.studiomdl)

def update_hlmv(self, context):
    self['hlmv'] = resolve(self.hlmv)

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
