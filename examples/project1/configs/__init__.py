import importlib
from pathlib import Path


i = 0
cfgs_list = []
for cfg in Path('configs').glob('*'):
    if not cfg.is_dir() and cfg.name[0] != '_':
        print(f'{i}: {cfg.name}')
        cfgs_list += [cfg.stem]
        i += 1

print('Choose a configuration file:')
k = input()

Config = importlib.import_module(f'configs.{cfgs_list[int(k)]}').Config
Config.init()