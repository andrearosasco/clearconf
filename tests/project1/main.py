from configs.main_config import Config as cfg
from configs.data_config import Data
import json

gt = {
    'Data(MyDataset)': 
        {
            'Eval(MyDataset)': {'split': 'eval'}, 
            'Train(MyDataset)': {'split': 'train'}, 
        'batch_size': 128, 
        'dataset_root': 'data/datasets/MyDataset', 
        'name': 'MyDataset_128', 'num_worker': 8
        }, 
    'Logging': 
        {
            'exp_dir': 'MyMethod_MyDataset_128', 
            'log_dir': 'logs', 
            'save_images': False
        },
    'Method(MyMethod)': 
        {
            'checkpoint': '../checkpoints/method.pt', 
            'device': 'cuda:0'
        }, 
    'root': '.'
    }

def main():
    cfg.Data = Data
    assert json.dumps(gt) == json.dumps(cfg.to_dict())
    

if __name__ == '__main__':
    main()