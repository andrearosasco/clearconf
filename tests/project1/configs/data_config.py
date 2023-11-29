from clearconf import BaseConfig
from dataset import MyDataset
from clearconf import Hidden

class MyDataset(BaseConfig):
    dataset_root = 'data/datasets/MyDataset'
    batch_size = 128
    num_worker: Hidden = 8
    
    class Train(MyDataset):
        split = 'train'
    class Eval(MyDataset):
        split = 'eval'

    name = '[eval]f"{cls.mro()[0].__name__}_{cls.batch_size}"'
    
Data = MyDataset

