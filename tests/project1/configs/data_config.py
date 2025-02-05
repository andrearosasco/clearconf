from clearconf import BaseConfig
from dataset import MyDataset
from clearconf import Hidden
from typing import Union

class MyDataset(BaseConfig):
    dataset_root = 'data/datasets/MyDataset'
    batch_size = 128
    num_worker: Union[Hidden, int] = 8
    
    class Train(MyDataset):
        split = 'train'
    class Eval(MyDataset):
        split = 'eval'

    name = '[eval]f"{cls.mro()[0].__name__}_{cls.batch_size}"'
    
Data = MyDataset

