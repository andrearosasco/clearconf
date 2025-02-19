from pathlib import Path
from clearconf import BaseConfig

project_root = Path('.')

class CommonConfig(BaseConfig):
        
    class Logging:
        exp_dir:str = '[eval]f"{cfg.Method._cc.name}_{cfg.Data.name}"'

    class Method:
        device:str = "cuda:0"


    
