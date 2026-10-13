import os
import stat
import sys
import tempfile
from unittest import TestCase, skipIf

from modcli import config
from tests.helpers import TokenHelper

TOKEN = TokenHelper.generate_token(exp=2000000000)


class CliContextTest(TestCase):

    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), 'modcli')
        context = config.CliContext(self.path)
        context.add_env('test', 'https://api.example.com/v2/', 'https://bundle.example.com/')
        context.set_active_env('test')
        context.current_env().set_token(TOKEN)
        context.save()

    def _file(self, name):
        return os.path.join(self.path, name)

    def test_save_and_read(self):
        env = config.CliContext.read(self.path).current_env()
        self.assertEqual((env.name, env.api_url, env.bundle_url), ('test', 'https://api.example.com/v2', 'https://bundle.example.com'))
        self.assertEqual((env.token, env.username, env.exp), (TOKEN, TokenHelper.USER_ID, 2000000000))
        with open(self._file('access_token')) as fh:
            self.assertEqual(fh.read().strip(), TOKEN)

    @skipIf(sys.platform == 'win32', 'POSIX permissions')
    def test_files_are_private(self):
        for name in ('context.json', 'access_token'):
            self.assertEqual(stat.S_IMODE(os.stat(self._file(name)).st_mode), 0o600)

    def test_clear(self):
        context = config.CliContext.read(self.path)
        context.clear()
        self.assertFalse(os.path.exists(self._file('context.json')))
        self.assertFalse(os.path.exists(self._file('access_token')))
        self.assertEqual(config.CliContext.read(self.path).environments, {})
