import torch


class ImageNet:

    def __init__(self, root = './data/PCN',
                split='PCN.json',
                subset='train',
                length=None,
                pick=[0]):
        self.i = 0
        self.length = length

    def __getitem__(self, idx):
        if self.i == self.length:
            raise StopIteration
        self.i += 1
        return torch.randn(8, 3), torch.randint(0, 1, size=(8, 1))

    def __len__(self):
        return self.length
