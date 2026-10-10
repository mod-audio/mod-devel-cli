import threading
import time
import urllib.request
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError

from modcli import pages, token_receiver


def _get(port: int, path: str) -> int:
    try:
        with urllib.request.urlopen(f'http://localhost:{port}{path}') as response:
            return response.status
    except HTTPError as e:
        return e.code


class ReceiveTokenTest(TestCase):

    def _receive(self, paths, state='s1', pasted=None, timeout=3):
        '''Run receive_token while a thread sends the browser requests in `paths`.
        `pasted` is what the user types; None leaves stdin empty.'''
        def fake_input():
            if pasted is None:
                raise EOFError
            time.sleep(0.3)
            return pasted

        port = token_receiver.get_open_port()
        statuses = []

        def browser():
            time.sleep(0.5)
            statuses.extend(_get(port, path) for path in paths)

        thread = threading.Thread(target=browser, daemon=True)
        thread.start()
        with patch('builtins.input', fake_input):
            result = token_receiver.receive_token(port, timeout, state)
        thread.join(timeout=1)
        return result, statuses

    def test_browser_token_with_matching_state(self):
        result, statuses = self._receive(['/?token=good&state=s1'])
        self.assertEqual(result, ('good', 'browser'))
        self.assertEqual(statuses, [200])

    def test_invalid_requests_are_ignored(self):
        paths = ['/favicon.ico', '/?state=s1', '/?token=bad&state=wrong', '/?token=bad', '/?token=good&state=s1']
        result, statuses = self._receive(paths)
        self.assertEqual(result, ('good', 'browser'))
        self.assertEqual(statuses, [400, 400, 400, 400, 200])

    def test_pasted_token(self):
        result, _ = self._receive([], pasted='  pasted-token \n')
        self.assertEqual(result, ('pasted-token', 'paste'))

    def test_blank_paste_is_ignored(self):
        result, _ = self._receive(['/?token=good&state=s1'], pasted='   ')
        self.assertEqual(result, ('good', 'browser'))

    def test_timeout(self):
        result, _ = self._receive([], timeout=1)
        self.assertEqual(result, (None, None))

    def test_local_url(self):
        self.assertEqual(token_receiver.local_url(1234), 'http://localhost:1234')


class PagesTest(TestCase):

    def test_pages_render(self):
        for page in (pages.signed_in(), pages.sign_in_failed()):
            html = page.decode('utf-8')
            self.assertTrue(html.startswith('<!doctype html>'))
            self.assertNotIn('$', html)
