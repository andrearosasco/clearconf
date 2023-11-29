
    
class MyDataset:
    def __init__(self) -> None:
        assert self.split in ['eval', 'train']
        assert self.parent.batch_size == 128