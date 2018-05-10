import json
import os
import stat
from datetime import datetime

from modcli import settings


def _get_config_dir():
    if not os.path.isdir(settings.CONFIG_DIR):
        os.makedirs(settings.CONFIG_DIR)
    return settings.CONFIG_DIR


def save_token(token: str, username: str, api_url: str):
    for path in [settings.TOKEN_PATH, settings.INFO_PATH]:
        if os.path.isfile(path):
            os.remove(path)
    with os.fdopen(os.open(settings.TOKEN_PATH, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
        fh.write(token)
        fh.write(os.linesep)
    data = {
        'token_path': settings.TOKEN_PATH,
        'username': username,
        'created': str(datetime.utcnow()),
        'remote': api_url,
    }
    with os.fdopen(os.open(settings.INFO_PATH, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
        fh.write(json.dumps(data))
        fh.writelines(os.linesep)


def read_token():
    if not os.path.isfile(settings.TOKEN_PATH):
        return None
    with open(settings.TOKEN_PATH, 'r') as fh:
        return fh.read().strip()
