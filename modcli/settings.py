import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

API_BASE_URL = os.environ.get('MOD_API_BASE_URL', 'https://api.moddevices.com/v2/').rstrip('/')
DEV_API_BASE_URL = os.environ.get('MOD_DEV_API_BASE_URL', 'https://api-dev.moddevices.com/v2/').rstrip('/')
API_KEY_PATH = os.path.join(_ROOT, 'mod_api_key.pub')
