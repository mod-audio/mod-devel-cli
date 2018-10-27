import os
from modcli import config

__version__ = '1.1.1'

# http://click.pocoo.org/5/python3/
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

context = config.read_context()
