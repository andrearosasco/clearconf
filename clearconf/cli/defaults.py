import typer

app = typer.Typer()

@app.command()
def add(script: str, config: str):
    if config[-3:] != '.py':
        print('Failed: Configurations have to be python files')
        return

    config = config[:-3]

    cconf_conf_path = find_cconf_config()
    cconf_conf = load_cconf_config(cconf_conf_path)

    cconf_conf['default'][script] = config
    save_cconf_config(cconf_conf, cconf_conf_path)