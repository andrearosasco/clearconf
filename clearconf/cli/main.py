import shutil
from pathlib import Path
import os

import confort

import typer

app = typer.Typer()

stub_path = Path(os.path.abspath(confort.__file__)).parent / "stubs/config.py"


@app.command()
def init():
    cfg_root = Path('configs')
    if cfg_root.exists():
        raise FileExistsError(f'Directory {cfg_root.as_posix()} already exists.')

    cfg_root.mkdir()
    (cfg_root / '__init__.py').touch()
    print(stub_path)
    shutil.copy(stub_path, cfg_root)

    print(f"Create confort .config file")


@app.callback()
def doc():
    """
    confort CLI can be used to initialized your
    project configurations.
    """


def main():
    app()


