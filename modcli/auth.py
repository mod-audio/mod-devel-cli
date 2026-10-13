import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.metadata import version
from urllib import parse

import click
from click import Abort

from modcli import http


def login(username: str, password: str, api_url: str):
    result = http.post(f'{api_url}/users/tokens', json_data={
        'user_id': username,
        'password': password,
        'agent': f'modcli:{version("mod-devel-cli")}',
    })
    if result.status_code != 200:
        raise Exception(f'Error: {result.json()["error-message"]}')
    return result.json()['message'].strip()


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def login_sso_detached(api_url: str):
    click.echo('Running in detached mode...')
    click.echo(f'1) Open this url in any browser: {api_url}/users/tokens_sso')
    click.echo('2) The URL will automatically redirect to MOD Forum (https://forum.mod.audio)')
    click.echo('3) Once MOD Forum page loads, if asked, enter your credentials or register a new user')
    click.echo('4) A JWT token will be displayed in your browser')
    try:
        token = click.prompt('Copy the token value and paste it here, then press ENTER')
        return token.strip()
    except Abort:
        sys.exit(1)


def login_sso(api_url: str):
    server_host = 'localhost'
    server_port = get_open_port()
    local_server = f'http://{server_host}:{server_port}'

    class SSORequestHandler(BaseHTTPRequestHandler):
        token = ''

        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            response = self.handle_http(200)
            _, _, _, query, _ = parse.urlsplit(self.path)
            result = parse.parse_qs(query)
            tokens = result.get('token', None)
            SSORequestHandler.token = tokens[0] if len(tokens) > 0 else None
            self.wfile.write(response)

        def handle_http(self, status_code):
            self.send_response(status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            content = '''
            <html><head><title>modcli - success</title></head>
            <body>Authentication successful! This browser window can be closed.</body></html>
            '''
            return bytes(content, 'UTF-8')

        def log_message(self, fmt, *args):
            pass

    httpd = HTTPServer((server_host, server_port), SSORequestHandler)
    httpd.timeout = 30

    click.echo('Open this URL in your browser to authenticate:')
    click.echo(f'{api_url}/users/tokens_sso?local_url={local_server}')

    try:
        httpd.handle_request()
    except KeyboardInterrupt:
        pass

    token = SSORequestHandler.token
    if not token:
        raise Exception('Authentication failed!')
    return token
