from .common_config import CommonConfig, project_root
from method import MyMethod

class Config(CommonConfig):

    class Method(MyMethod):
        checkpoint = project_root / '../checkpoints/method.pt'
