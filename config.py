import yaml


cfg = None

def load_config():
    global cfg

    if not cfg:
        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)

    return cfg
