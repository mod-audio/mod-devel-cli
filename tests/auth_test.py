from unittest import TestCase
from unittest.mock import patch
from urllib import parse

from modcli import auth
from tests.helpers import FakePost

API = 'https://api.example.com/v2'
LOCAL_URL = 'http://localhost:1234'


class LoginTest(TestCase):

    def test_login(self):
        post = FakePost(body='{"message": " the-token "}')
        with patch('modcli.http.post', post):
            self.assertEqual(auth.login('user', 'secret', API), 'the-token')
        url, data = post.calls[0]
        self.assertEqual(url, f'{API}/users/tokens')
        self.assertEqual((data['user_id'], data['password']), ('user', 'secret'))

    def test_login_error(self):
        with patch('modcli.http.post', FakePost(401, '{"error-message": "bad credentials"}')):
            with self.assertRaisesRegex(Exception, 'bad credentials'):
                auth.login('user', 'wrong', API)


class BrowserLoginUrlsTest(TestCase):

    def test_forum_url(self):
        base, query = auth.forum_url(API, LOCAL_URL, 'nonce').split('?')
        self.assertEqual(base, f'{API}/users/tokens_modforum')
        self.assertEqual(parse.parse_qs(query), {'local_url': [LOCAL_URL], 'state': ['nonce']})

    def test_google_url(self):
        base, query = auth.google_url(API, LOCAL_URL, 'nonce').split('?')
        self.assertEqual(base, f'{API}/users/tokens_google')
        self.assertEqual(parse.parse_qs(query), {'aud': ['api'], 'local_url': [LOCAL_URL], 'state': ['nonce']})


class MagicLinkTest(TestCase):

    def test_send_magic_link(self):
        post = FakePost(body='{"success": true, "expires_in": 900}')
        with patch('modcli.http.post', post):
            self.assertEqual(auth.send_magic_link(API, 'a@b.c', LOCAL_URL, 'nonce'), 900)
        self.assertEqual(post.calls, [(f'{API}/users/tokens_magiclink', {
            'email': 'a@b.c', 'aud': 'api', 'local_url': LOCAL_URL, 'state': 'nonce',
        })])

    def test_send_magic_link_error(self):
        with patch('modcli.http.post', FakePost(400, '{"error-message": "Email not registered"}')):
            with self.assertRaisesRegex(Exception, 'Email not registered'):
                auth.send_magic_link(API, 'x@b.c', LOCAL_URL, 'nonce')
