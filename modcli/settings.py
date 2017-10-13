import os

CONFIG_DIR = os.path.expanduser('~/.config/modcli')
TOKEN_PATH = os.path.join(CONFIG_DIR, 'access_token')

API_URL = os.environ.get('MOD_API_URL', 'https://api.moddevices.com/v2/').rstrip('/')
