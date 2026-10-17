import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

from modcli import pages


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def local_url(port: int):
    return f'http://localhost:{port}'


def receive_token(port: int, timeout: int, state: str):
    '''Return (token, source) for the first token received, either from the
    browser redirect to http://localhost:{port} carrying the expected state,
    source 'browser', or typed into stdin, source 'paste'. (None, None) on
    timeout. Requests without a valid token (a browser's favicon, a missing or
    wrong state, e.g. a web page probing localhost) are answered and ignored.'''
    received = {}
    done = threading.Event()

    def accept(token, source):
        received.setdefault('token', token.strip())
        received.setdefault('source', source)
        done.set()

    class TokenRequestHandler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            query = parse.parse_qs(parse.urlsplit(self.path).query)
            token = query.get('token', [None])[0]
            if token and query.get('state', [None])[0] == state:
                accept(token, 'browser')
                self._respond(200, pages.signed_in())
            else:
                self._respond(400, pages.sign_in_failed())

        def _respond(self, status_code, content):
            self.send_response(status_code)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, fmt, *args):
            pass

    def read_pasted_token():
        try:
            token = input()
        except EOFError:
            return
        if token.strip():
            accept(token, 'paste')

    httpd = HTTPServer(('localhost', port), TokenRequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    # a pending input() can't be cancelled; the daemon thread is dropped when the command exits
    threading.Thread(target=read_pasted_token, daemon=True).start()
    try:
        done.wait(timeout)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        httpd.server_close()

    return received.get('token'), received.get('source')
