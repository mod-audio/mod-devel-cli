import json
import os
import stat

import re

from modcli import settings


def read_context():
    context = CliContext.read(settings.CONFIG_DIR)
    if len(context.environments) == 0:
        for env_name, url in settings.API_URLS.items():
            context.add_env(env_name, url)
        context.set_active_env(settings.DEFAULT_ENV)
        context.save()
    return context


def _write_json_file(path: str, data: dict, remove_existing: bool=True):
    # create dir if doesn't exist
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)
    # remove previous file
    if remove_existing:
        if os.path.isfile(path):
            os.remove(path)
    # write json file
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR | stat.S_IWUSR), 'w') as fh:
        fh.write(json.dumps(data))
        fh.writelines(os.linesep)


def _read_json_file(path: str):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as file:
        contents = file.read()
    return json.loads(contents)


class CliContext(object):
    _filename = 'context.json'

    @staticmethod
    def read(path: str):
        context = CliContext(path)
        data = _read_json_file(os.path.join(path, CliContext._filename))
        if not data:
            return context
        for env in data['environments']:
            context.add_env(env['name'], env['url'])
            context.set_token(env['name'], env['username'], env['token'])
        context.set_active_env(data['active_env'])
        return context

    def __init__(self, path: str):
        self._path = path
        self._active_env = ''
        self.environments = {}

    def _ensure_env(self, env_name: str):
        if env_name not in self.environments:
            raise Exception('Environment {0} doen\'t exist'.format(env_name))

    def set_active_env(self, env_name: str):
        if not env_name:
            self._active_env = ''
        else:
            self._ensure_env(env_name)
            self._active_env = env_name

    def add_env(self, env_name: str, url: str):
        if not env_name:
            raise Exception('Environment name is invalid')
        if env_name in self.environments:
            raise Exception('Environment {0} already exists'.format(env_name))
        if not re.match('https?://.*', url):
            raise Exception('Invalid api_url: {0}'.format(url))

        self.environments[env_name] = EnvSettings(env_name, url)

    def remove_env(self, env_name: str):
        self._ensure_env(env_name)
        del self.environments[env_name]

    def set_token(self, env_name: str, username: str, token: str):
        self._ensure_env(env_name)
        self.environments[env_name].username = username
        self.environments[env_name].token = token

    def active_token(self):
        return self.environments[self._active_env].token

    def save(self):
        data = {
            'active_env': self._active_env,
            'environments': list({
                'name': e.name,
                'url': e.url,
                'username': e.username,
                'token': e.token,
            } for e in self.environments.values())
        }
        _write_json_file(os.path.join(self._path, CliContext._filename), data)


class EnvSettings(object):

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url.rstrip('/')
        self.username = ''
        self.token = ''
