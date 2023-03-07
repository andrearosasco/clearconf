from pathlib import Path
from confort import BaseConfig
from models import MLP
from datasets import ImageNet
from torch.optim import Adam
from torch.nn import BCEWithLogitsLoss

class Config(BaseConfig):
    name = Path(__file__).parts[-1]
    seed = 1234

    class Model(MLP):
        name = 'model.MLP'

        class Params:
            num_layers = 16
            layers_dim = [96] * num_layers

    class Data:
        input_dimension = 16384 * 2
        split = [0.1, 0.4, 0.5]
        noise_rate = 0.1
        tolerance = 0.001

        class DataSet:
            dataset = ImageNet

            class Params:
                root = './data/PCN'
                split = 'PCN.json'
                subset = 'train'
                length = 10
                pick = [0]

    class Train:
        loss_fn = BCEWithLogitsLoss()
        device = 'cuda'
        epochs = int(50_000)

        class Optim:
            optim = Adam

            class Params:
                lr = 0.0001


if __name__ == '__main__':
    Config.init()

    from experiments import training as exp
