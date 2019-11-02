import os

from ..utils.valve_utils import MaterialPathResolver, KeyValueFile, GameInfoFile

from pathlib import Path

if os.environ.get('VProject', None):
    del os.environ['VProject']


class VMT:

    def _get_proj_root(self, path: Path):
        if path.parts[-1] == 'materials':
            return path.parent
        else:
            return self._get_proj_root(path.parent)

    def __init__(self, filepath = None, game_dir=None, file = None):
        if file is not None:
            if not game_dir:
                game_dir = self._get_proj_root(self.filepath)
            os.environ['VProject'] = str(game_dir)
            self.textures = {}
            self.kv = KeyValueFile(file=file)
        else:
            self.filepath = Path(filepath)
            if not game_dir:
                game_dir = self._get_proj_root(self.filepath)
            os.environ['VProject'] = str(game_dir)
            self.textures = {}
            self.kv = KeyValueFile(filepath=filepath)
            
        self.shader = self.kv.root_chunk.key
        self.material_data = self.kv.as_dict[self.shader]
        gameinfo_path = game_dir / 'gameinfo.txt'
        if gameinfo_path.is_file():
            self.gameinfo = GameInfoFile(gameinfo_path)
        else:
            # We might not be dealing with a Source installation.
            # Use material path instead
            self.gameinfo = MaterialPathResolver(game_dir)

    def parse(self):
        print(self.shader)
        for key, value in self.material_data.items():
            if isinstance(value, str):
                texture = self.gameinfo.find_texture(value)
                if texture:
                    self.textures[key] = texture
                else:
                    if value.find("/") != -1:
                        self.textures[key] = value
