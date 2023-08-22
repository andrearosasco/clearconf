import __main__
import collections
import inspect
import json
from functools import partial
from typing import Generic
import copy

import types
def copy_func(f, name=None):
    return types.FunctionType(f.func_code, f.func_globals, name or f.func_name,
        f.func_defaults, f.func_closure)

def resolve(cls, body):
    cfg = find_root(cls)
    return eval(body) 

class _NestedClassGetter(object):
    """
    When called with the containing class as the first argument, 
    and the name of the nested class as the second argument,
    returns an instance of the nested class.
    """
    def __call__(self, containing_class, class_name):
        nested_class = getattr(containing_class, class_name)

        # make an instance of a simple object (this one will do), for which we can change the
        # __class__ later on.
        nested_instance = _NestedClassGetter()

        # set the class of the instance, the __init__ will never be called on the class
        # but the original state will be set later on by pickle.
        nested_instance.__class__ = nested_class
        return nested_instance


class Watcher(type):
    def __init__(cls, name, bases, clsdict):
        # This is first called for BaseConfig, then for Config
        # After subclass is called, or the classes defined insided Config inherit
        # from BaseConfig and this is called for those too.
        
        # This allows us to propagate BaseConfig deeper.
        if len(cls.mro()) > 2:
            cls._subclass()
        super(Watcher, cls).__init__(name, bases, clsdict)

def find_root(target):
    while True:
        try:
            target = target.parent
        except AttributeError:
            return target

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
        for attr in [a for a in target.mro() 
                     if a.__name__ not in [target.__name__, f'{target.__name__}_mod', target.__name__[:-4], 'BaseConfig', 'Config', 'object']]:
            # The allows inheritance between configs but I guess there are better solutions
            if 'configs' not in attr.__module__:
                target_attr = target_attr - set(dir(attr))

        for k in target_attr:
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg', 'parent']:
                attr = getattr(target, k)
                
                if type(attr).__name__ == 'property':
                    attr = attr.fget

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
                            res[k] = f'function: {attr.__name__}'
                    elif attr.__module__.split('.')[0] == '__main__' or 'config' in attr.__module__:
                        if not inspect.isclass(attr): attr = type(attr)
                        
                        subclass_names = [a for a in [a.__name__ for a in attr.mro()] 
                                     if a not in [k, 'BaseConfig', 'object']]
                        
                        if len(subclass_names) > 0: # when a config class is subclassed to use it directly
                            k = f'{k}({subclass_names[0]})'

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
        
        #  Give a name to the class
        subclass_names = [a for a in [a.__name__ for a in target.mro()] if a not in [target.__name__, 'BaseConfig', 'object']]
        if len(subclass_names) > 0:
            _name = f'{_name}:{subclass_names[0]}'
        setattr(target, '_name', _name)

        res = {}
        for k in dir(target):
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg', 'parent', '_name']:
                attr = getattr(target, k)
                
                if isinstance(attr, str) and attr.startswith('[eval]'):
                    body = copy.deepcopy(attr[6:])
                    setattr(target, k, classmethod(property(partial(resolve, body=body))))
                
                # If it's a class inside config, get inside it,
                # else just log module and name in the dict as a string
                if hasattr(attr, '__module__') and type(attr).__name__ != 'function':
                    
                    # if we are executing the config the module is __main__. If we are importing it is config
                    # Not ideal but config could be anywhere in the name
                    # Need to find a better way to do this
                    
                    # All of this could be probably brought out of the for loop as _subclass is called
                    # for all the nested classes
                    if attr.__module__.split('.')[0] == '__main__' or 'config' in attr.__module__:
                        # This way the module keeps its subclasses but it is also subclassed by
                        # BaseConfig inheriting its method. A security check could be used to assure
                        # that the new methods are not overriding any old one.
                        
                        if 'BaseConfig' not in [a.__name__ for a in attr.mro()]:
                            if Generic in (base_classes := attr.mro()): base_classes.remove(Generic)
                            setattr(target, k, type(k, (BaseConfig, ) + tuple(base_classes), dict(list(dict(vars(BaseConfig)).items()) + list(dict(vars(attr)).items()))))
                            
                            def _pickle_reduce(self):
                                # return a class which can return this class when called with the 
                                # appropriate tuple of arguments
                                state = self.__dict__.copy()
                                return (_NestedClassGetter(), (target, self.__class__.__name__, ), state)
                            setattr((getattr(target, k)), '__reduce__', _pickle_reduce)
                        
                        setattr((getattr(target, k)), 'parent', target)
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
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg', 'parent']:
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
        for attr in [a for a in target.mro() 
                     if a.__name__ not in [target.__name__, target.__name__[:-4], 'BaseConfig', 'Config', 'object']]:
            # The allows inheritance between configs but I guess there are better solutions
            if 'configs' not in attr.__module__:
                target_attr = target_attr - set(dir(attr))
        
        for k in target_attr:
            if not k.startswith('_') and k not in ['to_dict', 'to_json', 'to_list', 'init', 'to_flat_dict', 'get_cfg', 'parent']:
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