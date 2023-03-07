import abc
import importlib
from pathlib import Path
import builtins

noop = True

class NoOpMeta(abc.ABCMeta):

    def __getattribute__(cls, item):
        try:
            return abc.ABCMeta.__getattribute__(cls, item)
        except AttributeError as e:
            if noop:
                return NoOp
            else:
                raise e


class NoOp(metaclass=NoOpMeta):
    pass
    # def __getattribute__(self, item):
    #     return self.__getattribute__(self, item)


# This solves circular imports (see project2)
def _import(name, *args, **kwargs):
    if name.split('.')[0] == 'configs':
        return NoOp
    return original_import(name, *args, **kwargs)


original_import = builtins.__import__
builtins.__import__ = _import

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

for k in dir(Config):
    if not k.startswith('__'):
        setattr(NoOp, k, getattr(Config, k))

noop = False
builtins.__import__ = original_import