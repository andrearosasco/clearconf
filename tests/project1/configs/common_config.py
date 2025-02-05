from pathlib import Path
from clearconf import BaseConfig

project_root = Path('.')

class CommonConfig(BaseConfig):
    root = project_root
        
    class Logging:
        log_dir:Path = project_root / 'logs'
        exp_dir:str = f'[eval]f"{{cfg.Method._cc.name.split(\':\')[1]}}_{{cfg.Data.name}}"'

        save_images:bool = False

    class Method:
        device:str = "cuda:0"
