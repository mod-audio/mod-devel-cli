import os

CONFIG_DIR = os.path.expanduser('~/.config/modcli')
URLS = {
    'dev': ('https://api-dev.mod.audio/v2', 'https://pipeline-dev.mod.audio/bundle/'),
    'prod': ('https://api.mod.audio/v2', 'https://pipeline.mod.audio/bundle/')
}
DEFAULT_ENV = 'dev'
