from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from modcli import cli, config, context
from tests.helpers import TokenHelper

TOKEN = TokenHelper.generate_token(exp=2000000000, aud='api')
BROWSER_LOGINS = [
    (cli.login_sso, []),
    (cli.login_google, []),
    (cli.login_magiclink, ['--email', TokenHelper.USER_ID]),
]


class BrowserLoginTest(TestCase):

    def setUp(self):
        self.opened = []
        self.received = (TOKEN, 'browser')
        patches = [
            patch('webbrowser.open', self.opened.append),
            patch('modcli.token_receiver.receive_token', lambda port, timeout, state: self.received),
            patch('modcli.auth.send_magic_link', lambda *args: None),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_login_stores_token(self):
        for command, args in BROWSER_LOGINS:
            with self.subTest(command=command.name):
                result = CliRunner().invoke(command, args)
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn(f'You\'re now logged in as [{TokenHelper.USER_ID}]', result.output)
                self.assertEqual(context.active_token(), TOKEN)

    def test_login_opens_the_sign_in_url(self):
        CliRunner().invoke(cli.login_google, [])
        self.assertEqual(len(self.opened), 1)
        self.assertIn('aud=api', self.opened[0])

    def test_one_time_prints_token_only(self):
        result = CliRunner().invoke(cli.login_google, ['-o'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.strip().endswith(TOKEN))

    def test_failed_login_exits_with_error(self):
        self.received = (None, None)
        result = CliRunner().invoke(cli.login_google, [])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Authentication failed!', result.output)


class ConfirmAllTest(TestCase):

    def test_confirm_all_is_accepted_and_ignored(self):
        for command, args in [(cli.login, ['-u', 'user', '-p', 'secret']), *BROWSER_LOGINS]:
            with self.subTest(command=command.name):
                params = command.make_context(command.name, ['-y', *args]).params
                self.assertNotIn('confirm_all', params)


class SetTokenTest(TestCase):

    def test_set_token_decodes_base64url_payload(self):
        # A payload whose base64url encoding uses '-' or '_', which plain base64 decoding garbles
        user_id = next(f'user{i}?>' for i in range(1000)
                       if set('-_') & set(TokenHelper.generate_token(f'user{i}?>').split('.')[1]))
        env = config.EnvSettings('test', 'https://api', 'https://bundle')
        env.set_token(TokenHelper.generate_token(user_id))
        self.assertEqual(env.username, user_id)
