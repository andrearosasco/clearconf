from clearconf import BaseConfig, Hidden, Prompt
    

class cfg(BaseConfig):
    class Method:
        checkpoint: Hidden = '../checkpoints/method.pt'
        device = 'cuda:0'

# Call this like: python config.py --Method config.MyMethod
if __name__ == '__main__':
    cfg.Method()
    print(cfg.to_dict2()) # {'Method': {'checkpoint': '../checkpoints/method.pt', 'device': 'cuda:0'}}