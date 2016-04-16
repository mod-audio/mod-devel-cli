import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

API_BASE_URL = os.environ.get('MOD_API_BASE_URL', 'http://api.moddevices.com/v1/').rstrip('/')
MOD_API_KEY_PATH = os.path.join(_ROOT, 'mod_api_key.pub')
