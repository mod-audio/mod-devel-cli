import json
import os
import stat
from datetime import datetime

from modcli import settings


def _get_config_dir():
    if not os.path.isdir(settings.CONFIG_DIR):
        os.makedirs(settings.CONFIG_DIR)
    return settings.CONFIG_DIR


def _remove_files(files):
    for path in files:
        if os.path.isfile(path):
            os.remove(path)


def save_token(token: str, username: str, api_url: str, environment: str):
    token_paths = [
        os.path.join(settings.CONFIG_DIR, i)
        for i in ['access_token', '{0}.access_token'.format(environment)]
    ]
    info_paths = [
        os.path.join(settings.CONFIG_DIR, i)
        for i in ['info.json', '{0}.info.json'.format(environment)]
    ]
    _remove_files(token_paths + info_paths)

    for token_path in token_paths:
        with os.fdopen(os.open(token_path, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
            fh.write(token)
            fh.write(os.linesep)
    for info_path in info_paths:
        data = {
            'token_path': token_paths[1],
            'username': username,
            'created': str(datetime.utcnow()),
            'remote': api_url,
            'environment': environment,
        }
        with os.fdopen(os.open(info_path, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
            fh.write(json.dumps(data))
            fh.writelines(os.linesep)


def read_token(environment: str):
    token_filename = 'access_token' if environment is None else '{0}.access_token'.format(environment)
    token_path = os.path.join(settings.CONFIG_DIR, token_filename)
    if not os.path.isfile(token_path):
        return None
    with open(token_path, 'r') as fh:
        return fh.read().strip()
