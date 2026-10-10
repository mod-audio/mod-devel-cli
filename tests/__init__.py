import os
import tempfile

# Importing modcli reads (and creates) ~/.config/modcli, so point the home at a temp dir first
_home = tempfile.mkdtemp()
os.environ['HOME'] = _home
os.environ['USERPROFILE'] = _home
