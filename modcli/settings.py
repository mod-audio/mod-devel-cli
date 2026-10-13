import os

CONFIG_DIR = os.path.expanduser('~/.config/modcli')
URLS = {
    'labs': ('https://api-labs.mod.audio/v2', 'https://pipeline-labs.mod.audio/bundle/'),
    'dev': ('https://api-dev.mod.audio/v2', 'https://pipeline-dev.mod.audio/bundle/'),
}
DEFAULT_ENV = 'labs'
