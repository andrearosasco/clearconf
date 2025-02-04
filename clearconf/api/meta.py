from clearconf.api.exceptions import EvalError
from .node import Node
from clearconf.api.tree_functions import arg_parse, user_input


# TODO let's get rid of the node class as it offer helpers methods but create a 
# separate stracture that has to be kept consistent. All the helpers that we need can be contained 
# under the .cc attribute of every ClearConf class.

class MetaBaseConfig(type):
    def __init__(cls, name, bases, clsdict):
        '''This executes after the configuration subclassing baseconfig
           is defined and it adds BaseConfig as a super class of all nested
           configurations'''
        super(MetaBaseConfig, cls).__init__(name, bases, clsdict)
        cls._cc = type('_cc', tuple(), {})
        
        if vars(cls._cc).get('initialized', False):
            return

        try:
            # This will execute for the root config and all nested configurations 
            # as they are automatically set to be subclasses of BaseConfig
            if len(cls.mro()) > 2:
                cls.__visit()

            # This will only execute for the root config. Since the root config wraps
            # everything else, at this point all the configig should already be initialized
            if len(cls.mro()) == 3:
                arg_parse(cls)
                user_input(cls)  # check if any attributes have the Prompt flas
                
        except EvalError:
            # String evaluation error is deferred to user evaluation        
            pass
    
    def __visit(cls):
        from clearconf.api._utils.misc import (expand_name, add_parent, resolve_eval, subclass, add_function)
        from clearconf.api._utils.pickle_reduce import add_pickle_reduce
        from clearconf.api.tree_functions import to_dict, to_flat_dict, to_json, to_list, to_dict2
        from clearconf.api.node import is_config, is_hidden, is_private, is_visited

        cls._cc.initialized = False
        
        cls._name = expand_name(cls)
        cls._nodes = [Node(name, parent=cls) for name in dir(cls)]

        for fn in [to_dict, to_flat_dict, to_json, to_list, to_dict2]:
            add_function(cls, fn)

        for node in cls._nodes:
            subclass(node)
            add_parent(node) # if you add the parent before subclass an infinite loop happens
            resolve_eval(node)
            # add_pickle_reduce(node)

        cls._cc.initialized = True

    def _apply(cls, func):
        """Apply a function to all the leaves in the tree
           The function needs to have a compute and aggregate method.
           One will map a leaf node to a value and the outher will function as an accumulator"""

        final_res = None

        for node in cls._nodes:

            if node.is_config:
                res = node.value._apply(func)
            else:
                res = func.compute(node)

            final_res = res if final_res is None else func.aggregate(final_res, res)

        return final_res


    def __setattr__(cls, key, value):
        super().__setattr__(key, value)
        
        # This will let you add a baseconfig as an attribute of another while maintaining the tree
        if isinstance(value, MetaBaseConfig) and value._cc.initialized and cls._cc.initialized:
            value._name = f'{key}:{value._name}'
            node = Node(key, parent=cls, value=value)
            cls._nodes.append(node)

            if not node.is_config or node.is_hidden or node.is_private or node.name == 'parent':
                return
            node.value._parent = node.parent