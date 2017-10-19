import os
import stat

from modcli import settings


def _get_config_dir():
    if not os.path.isdir(settings.CONFIG_DIR):
        os.makedirs(settings.CONFIG_DIR)
    return settings.CONFIG_DIR


def save_token(token: str):
    if os.path.isfile(settings.TOKEN_PATH):
        os.remove(settings.TOKEN_PATH)
    with os.fdopen(os.open(settings.TOKEN_PATH, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
        fh.write(token)
        fh.write(os.linesep)


def read_token():
    if not os.path.isfile(settings.TOKEN_PATH):
        return None
    with open(settings.TOKEN_PATH, 'r') as fh:
        return fh.read().strip()
