import torch
import torch.nn as nn

from configs import Config

class MLP(nn.Module):

    def __init__(self):
        super().__init__()

        layers_dim = Config.Model.Params.layers_dim
        if not isinstance(layers_dim, list):
            layers_dim = [Config.Model.Params.layers_dim] * Config.Model.Patameters.num_layers

        self.input_lyr = nn.Linear(3, layers_dim[0])
        self.output_lyr = nn.Linear(layers_dim[-1], 1)

        lyr_list = []
        for i in range(len(layers_dim) - 1):
            lyr_list += [nn.Linear(layers_dim[i], layers_dim[i + 1])]

        self.hidden_lyrs = nn.Sequential(*lyr_list)

    def forward(self, x):
        x = torch.relu(self.input_lyr(x))
        for lyr in self.hidden_lyrs:
            x = torch.relu(lyr(x))
        out = self.output_lyr(x)

        return out
