import torch

from configs.Config import Data


class ImageNet:

    def __init__(self):
        self.i = 0
        self.length = Data.DataSet.Params.Length

    def __getitem__(self, idx):
        if self.i == self.length:
            raise StopIteration
        self.i += 1
        return torch.randn(8, 3), torch.randint(0, 1, size=(8, 1))

    def __len__(self):
        return self.length
