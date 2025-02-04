import copy
from functools import partial
from typing import Generic
from clearconf import BaseConfig, Hidden
from clearconf.api.exceptions import EvalError

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

def add_function(cls, fn):
    
    if isinstance(fn, classmethod):
        name = fn.__func__.__name__  # Necessary for python 3.9 where classmethods do not inherit __name__
    else:
        name = fn.__name__
    setattr(cls, name, fn)
    # cls.__annotations__[name] = Hidden


def find_root(target):
    if not issubclass(target, BaseConfig):
        return target
    while True:
        try:
            target = target._parent
        except AttributeError:
            return target

def resolve(cls, body):
    cfg = find_root(cls)
    try:
        return eval(body)
    except Exception as e:
        # return 'Error in eval string evaluation'
        raise EvalError(f'The eval string {body} couldn\'t be resolved') from e

def resolve_eval(node):
    '''if the attribute is a string starting with [eval] the rest of the
       string is evaluated and the result is substituted to the original
       attribute'''
    if node.is_private or node.is_hidden:
        return
       
    if isinstance(node.value, str) and node.value.startswith('[eval]'):
        body = copy.deepcopy(node.value[6:])
        node.value = classmethod(property(partial(resolve, body=body)))
    
def subclass(node, superclass=BaseConfig):
    if not node.is_config or node.is_visited or node.is_private or node.is_hidden or node.name == 'parent':
        return
    
    if Generic in (base_classes := node.value.mro()): base_classes.remove(Generic) # necessary to avoid errors with typing
    # this create a new class equals to attr but which subclass BaseConfig
    node.value = type(node.name,
                    tuple(base_classes[:-1]) + (superclass,) ,
                    dict(list(dict(vars(superclass)).items()) + list(dict(vars(node.value)).items()))
                )
    
    
def add_parent(node):
    if not node.is_config or node.is_hidden or node.is_private or node.name == 'parent':
        return

    node.value._parent = node.parent