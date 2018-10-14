import os

CONFIG_DIR = os.path.expanduser('~/.config/modcli')
API_URLS = {
    'labs': 'https://api-labs.moddevices.com/v2',
    'local': 'http://localhost:8000/v2',
}
DEFAULT_ENV = 'labs'
