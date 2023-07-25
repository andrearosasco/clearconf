import __main__
import collections
import inspect
import json
from pathlib import Path


class Watcher(type):
    def __init__(cls, name, bases, clsdict):
        # This is first called for BaseConfig, then for Config
        # After subclass is called, or the classes defined insided Config inherit
        # from BaseConfig and this is called for those too.
        
        # This allows us to propagate BaseConfig deeper.
        if len(cls.mro()) > 2:
            cls._subclass()
        super(Watcher, cls).__init__(name, bases, clsdict)

class BaseConfig(metaclass=Watcher):

    @classmethod
    def to_json(cls):
        return json.dumps(cls.to_dict())

    @classmethod
    def to_dict(cls, add_parent=False):
        target = cls

        # This add target as the top key of the dictionary
        #  if add_parent is True
        res = output = {}
        if add_parent:
            key = target.__name__
            if len(target.mro()) >= 4:
                key =  target.mro()[2].__name__
            if len(target.mro()) >= 5:
                key = f'{key}({target.mro()[3].__name__})'
            output = {key: res}

        target_attr = set(dir(target))
        # This removes variables from superclasses
        for i in range(3, len(target.__mro__) - 1):
            # The allows inheritance between configs but I guess there are better solutions
            if 'configs' not in target.__mro__[i].__module__:
                target_attr = target_attr - set(dir(target.__mro__[i]))

        for k in target_attr:
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg']:
                attr = getattr(target, k)

                # If it's a module get inside
                if hasattr(attr, '__module__'):

                    # If it's a class inside config, get inside it,
                    # else just log module and name in the dict as a string.

                    # if we are executing the config the module is __main__. If we are importing it is config
                    if type(attr).__name__ == 'function':
                        if attr.__name__ == '<lambda>':
                            funcString = str(inspect.getsourcelines(attr)[0])
                            res[k] = funcString.strip("['\\n']").split(" = ")[1]
                        else:
                            res[k] = f'function : {attr.__name__}'
                    elif attr.__module__.split('.')[0] == '__main__' or 'config' in attr.__module__:
                        if len(attr.mro()) >= 5: # when a config class is subclassed to use it directly
                            subclass_name = [a for a in [a.__name__ for a in attr.mro()] if a not in [k, f'{k}_Mod', 'BaseConfig']][0]
                            k = f'{k}({subclass_name})'
                        res[k] = attr.to_dict()
                    else:
                        # End up here if attr is not a class defined inside module.
                        if type(attr).__name__ == 'type':  # it is a class
                            name = f'{attr.__module__}.{attr.__name__}'
                        else: # it is an object
                            if attr.__str__ is not object.__str__:
                                name = attr.__str__()  # sometimes repr() might be preferable
                            else:
                                name = f'{type(attr).__name__}.{attr.__name__}'
                            res[k] = name
                # If it's not a class save it. This is done for basic types.
                # Could cause problems with complex objects
                else:
                    res[k] = attr

        return output

    @classmethod
    def _subclass(cls):

        target = cls

        res = {}
        for k in dir(target):
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg']:
                attr = getattr(target, k)
                # If it's a class inside config, get inside it,
                # else just log module and name in the dict as a string
                if hasattr(attr, '__module__') and type(attr).__name__ != 'function':

                    # if we are executing the config the module is __main__. If we are importing it is config
                    # Not ideal but config could be anywhere in the name
                    # Need to find a better way to do this
                    if attr.__module__.split('.')[0] == '__main__' or 'config' in attr.__module__:
                        # This way the module keeps its subclasses but it is also subclassed by
                        # BaseConfig inheriting its method. A security check could be used to assure
                        # that the new methods are not overriding any old one.
                        if 'BaseConfig' not in [a.__name__ for a in attr.mro()]:
                            setattr(target, k, type(f'{k}_mod', (BaseConfig, ) + tuple(attr.__mro__), dict(list(dict(vars(BaseConfig)).items()) + list(dict(vars(attr)).items()))))
        return res

    @classmethod
    def to_flat_dict(cls) -> dict:
        import torch
        res = cls.to_dict()
        res = flatten(res)
        return res

    @classmethod
    def to_list(cls):
        target = cls

        res = []
        for k in dir(target):
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg']:
                attr = getattr(target, k)
                # If it's a class inside config, get inside it,
                # else just log module and name in the dict as a string
                if type(attr) == type:
                    if attr.__module__.split('.')[0] in ['configs', '__main__']:
                        res.append(attr.to_list())
                    else:
                        res.append(f'{attr.__module__}.{attr.__name__}')
                # If it's not a class save it. This is done for basic types.
                # Could cause problems with complex objects
                else:
                    res.append(attr)
        return res
    
    def get_cfg(self, to_self=False):
        if not to_self:
            return self.__class__
        
        target = self.__class__
        
        target_attr = set(dir(target))
        # This removes variables from superclasses
        for i in range(3, len(target.__mro__) - 1):
            # The allows inheritance between configs but I guess there are better solutions
            if 'configs' not in target.__mro__[i].__module__:
                target_attr = target_attr - set(dir(target.__mro__[i]))
        
        for k in target_attr:
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg']:
                attr = getattr(target, k)
                setattr(self, k, attr)
    
    def __getattribute__(self, item):
        return object.__getattribute__(self, item)


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)