import inspect
from clearconf.api.types import Hidden

# @property
def is_private(value, name, parent):
    return name.startswith('_') or '._' in name

def is_type(value, name, parent, cc_type):
    actual_type = getattr(parent, '__annotations__', {}).get(name, None)    
    # if __args__ is present it is a UnionType and we check if cc_type is in it
    # otherwise we return a list containing its only type and check if it is cc_type
    return cc_type in getattr(actual_type, '__args__', [actual_type])

# @property
def is_hidden(value, name, parent):
    from clearconf.api.base_config import BaseConfig
    return name in dir(BaseConfig) or is_type(value, name, parent, Hidden)

      
# @property      
def is_visited(value, name, parent):
    from clearconf.api.base_config import BaseConfig
    return issubclass(value, BaseConfig)

# @property
def is_config(value, name, parent):
    from clearconf.api.base_config import BaseConfig
    from clearconf.api._utils.misc import find_root
    # Attr is a class who has either been defined in the same module we are considering or is a
    # subclass of BaseConfig
    return (inspect.isclass(value) and 
        (value.__module__ == parent.__module__ or issubclass(value, BaseConfig)) and name != 'parent')
    