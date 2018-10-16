import os

CONFIG_DIR = os.path.expanduser('~/.config/modcli')
URLS = {
    'labs': ('https://api-labs.moddevices.com/v2', 'https://pipeline-labs.moddevices.com/bundle/'),
    'dev': ('https://api-dev.moddevices.com/v2', 'https://pipeline-dev.moddevices.com/bundle/'),
}
DEFAULT_ENV = 'labs'
