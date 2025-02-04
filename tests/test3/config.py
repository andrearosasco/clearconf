import datetime
from clearconf import BaseConfig

class Config(BaseConfig):
    dataset = 'full_80'
    checkpoint = 'checkpoint1'
    model = 'transformer'
    method = 'dbts'
    task = ''
    start_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    checkpoint = '[eval]f"data/weights/diffusion_{cfg.model}_{cfg.task}/checkpoints/{cfg.dataset}/{cfg.checkpoint}.ckpt"'
    output_dir = '[eval]f"data/evaluations/diffusion_\
                          {cfg.model}_{cfg.task}/{cfg.dataset}/{cfg.checkpoint}/{start_time}_\
                          {cfg.method}_horizon_{cfg.hotizon}_tta_{cfg.tta}"'
    device = 'cuda:0'

    horizon = 15 # transformer: 9
    tta = 'none'  # flip, color_jitter, rotate


    class Filter:
        name = 'dbts'
        kwargs = {}

print('Configuration Loaded')
print(Config.to_dict())
