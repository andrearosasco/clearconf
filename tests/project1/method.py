
class MyMethod:
    def __init__(self) -> None:
        assert self.device == 'cuda'
        assert self.parent.Logging.save_images == False