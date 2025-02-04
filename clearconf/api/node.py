import inspect
import typing
# from types import UnionType

from clearconf.api.types import Hidden


class Node:
    
    def __init__(self, name, parent=None, value=None) -> None:
        self._name = name
        self._alias = name
        
        if parent is None:
            parent = type('parent', (), {})
            setattr(parent, name, value)
        
        self.parent = parent
        
    @property
    def value(self):
        return getattr(self.parent, self._name)
        
    @value.setter
    def value(self, new):
        setattr(self.parent, self._name, new)
        
    @property
    def name(self):
        return self._alias
    
    @name.setter
    def name(self, alias):
        self._alias = alias
        
    @property
    def is_private(self):
        return self.name.startswith('_') or '._' in self.name

    def is_type(self, cc_type):
        actual_type = self.parent.__dict__.get('__annotations__', {}).get(self.name, None)    
        # if __args__ is present it is a UnionType and we check if cc_type is in it
        # otherwise we return a list containing its only type and check if it is cc_type
        return cc_type in getattr(actual_type, '__args__', [actual_type])
    
    @property
    def is_hidden(self):
        from clearconf.api.base_config import BaseConfig
        return self.name in dir(BaseConfig) or self.is_type(Hidden)
    
    
    @property      
    def is_visited(self):
        from clearconf.api.base_config import BaseConfig
        return issubclass(self.value, BaseConfig)
    
    @property
    def is_config(self):
        from clearconf.api.base_config import BaseConfig
        from clearconf.api._utils.misc import find_root
        # Attr is a class who has either been defined in the same module we are considering or is a
        # subclass of BaseConfig
        return (inspect.isclass(self.value) and 
            (find_root(self.value).__module__ == self.parent.__module__ or issubclass(self.value, BaseConfig)) and self.name != '_parent')
        
    def __repr__(self):
        return f'clearconf.Node({self.name})'

@property
def is_private(cls):
    return cls.name.startswith('_') or '._' in cls.name

def is_type(cls, cc_type):
    actual_type = cls.parent.__dict__.get('__annotations__', {}).get(cls.name, None)    
    # if __args__ is present it is a UnionType and we check if cc_type is in it
    # otherwise we return a list containing its only type and check if it is cc_type
    return cc_type in getattr(actual_type, '__args__', [actual_type])

@property
def is_hidden(cls):
    from clearconf.api.base_config import BaseConfig
    return cls.name in dir(BaseConfig) or cls.is_type(Hidden)


@property      
def is_visited(cls):
    from clearconf.api.base_config import BaseConfig
    return issubclass(cls.value, BaseConfig)

@property
def is_config(cls):
    from clearconf.api.base_config import BaseConfig
    from clearconf.api._utils.misc import find_root
    # Attr is a class who has either been defined in the same module we are considering or is a
    # subclass of BaseConfig
    return (inspect.isclass(cls.value) and 
        (find_root(cls.value).__module__ == cls.parent.__module__ or issubclass(cls.value, BaseConfig)) and cls.name != '_parent')
    