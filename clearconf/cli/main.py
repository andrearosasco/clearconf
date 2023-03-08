import shutil
from pathlib import Path
import os

import clearconf
import typer
import json

from clearconf.cli.utils.file import find_config, load_config

app = typer.Typer()

stub_path = Path(os.path.abspath(clearconf.__file__)).parent / "stubs/config.py"


@app.command()
def init():
    cfg_root = Path('configs')
    if cfg_root.exists():
        raise FileExistsError(f'Directory {cfg_root.as_posix()} already exists.')

    cfg_root.mkdir()
    (cfg_root / '__init__.py').touch()
    shutil.copy(stub_path, cfg_root)

    cconf_configs = Path('.clearconf')
    if cconf_configs.exists():
        raise FileExistsError(f'File {cconf_configs.as_posix()} already exists.')

    cconf_configs.touch()

    content = {'cfg_root': cfg_root.as_posix()}
    with cconf_configs.open('w+') as f:
        json.dump(content, f, indent=4)
        f.write('\n')

@app.command()
def list():
    cconf_conf_path = find_config()
    cconf_conf = load_config(cconf_conf_path)

    # List all files ending with _cfg in the cfg_root directory
    for file in Path(cconf_conf['cfg_root']).glob('*'):
        print(file)



@app.callback()
def doc():
    """
    confort CLI can be used to initialized your
    project configurations.
    """


def main():
    app()


