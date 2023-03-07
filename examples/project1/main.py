import tqdm as tqdm

from configs import Config

def main():

    Model = Config.Model
    Data = Config.Data
    Train = Config.Train

    model = Model(**Config.Model.Params.to_dict())
    dataset = Data.DataSet.dataset(**Config.Data.DataSet.Params.to_dict())

    model.train()
    model.to(Train.device)

    optimizer = Train.Optim.optim(model.parameters(), **Train.Optim.Params.to_dict())

    for i in tqdm.tqdm(range(Train.epochs)):

        for x, y in dataset:
            x = x.to(Train.device)
            predictions = model(x)


if __name__ == '__main__':
    main()
