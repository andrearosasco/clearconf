import copy
from functools import partial
from typing import Generic
from clearconf import BaseConfig, Hidden
from clearconf.api.exceptions import EvalError
from clearconf.api.node import is_config, is_hidden, is_private, is_visited

def expand_name(target):
    superclasses = list(filter(lambda x: x not in [target.__name__, 'BaseConfig', 'object'], 
                        map(lambda x: x.__name__, target.mro())))
    if len(superclasses) > 0:
        return f'{target.__name__}:{superclasses[0]}'
    return target.__name__

# def expand_name(node):
#     if not node.is_config or node.is_hidden or node.is_private:
#         return
    
#     superclasses = list(filter(lambda x: x not in [node.name, 'BaseConfig', 'object'], 
#                         map(lambda x: x.__name__, node.value.mro())))

    # if len(superclasses) > 0:
    #     node.name =  f'{node.name}:{superclasses[0]}'
    # node.value.__name__ = node.name

def add_function(cls, fn, hidden=False):
    
    if isinstance(fn, classmethod):
        name = fn.__func__.__name__  # Necessary for python 3.9 where classmethods do not inherit __name__
    elif isinstance(fn, property):
        name = fn.fget.__name__
    else:
        name = fn.__name__
    setattr(cls, name, fn)
    if not hidden:
        return

    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = {}

    cls.__annotations__[name] = Hidden


def find_root(target):
    if not issubclass(target, BaseConfig):
        return target
    while True:
        try:
            target = target._cc.parent
        except AttributeError:
            return target

def resolve(cls, body):
    cfg = find_root(cls)
    try:
        return eval(body)
    except Exception as e:
        # return 'Error in eval string evaluation'
        raise EvalError(f'The eval string {body} couldn\'t be resolved') from e

def resolve_eval(value, name):
    '''if the attribute is a string starting with [eval] the rest of the
       string is evaluated and the result is substituted to the original
       attribute'''
       
    if isinstance(value, str) and value.startswith('[eval]'):
        body = copy.deepcopy(value[6:])
        value = classmethod(property(partial(resolve, body=body)))
    return value
    
def subclass(value, name, parent, superclass=BaseConfig):
    if not is_config(value, name, parent) or is_visited(value, name, parent) or is_private(value, name, parent) or is_hidden(value, name, parent) or name == 'parent':
        return value

    if Generic in (base_classes := value.mro()): base_classes.remove(Generic) # necessary to avoid errors with typing
    # this create a new class equals to attr but which subclass BaseConfig
    value = type(name,
                    tuple(base_classes[:-1]) + (superclass,) ,
                    dict(list(dict(vars(superclass)).items()) + list(dict(vars(value)).items()))
                )
    return value
    
    
def add_parent(value, name, parent):
    if not is_config(value, name, parent) or is_hidden(value, name, parent) or is_private(value, name, parent) or name == 'parent':
        return value
    
    value._cc.parent = parent
    return value