import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import click
import crayons
import requests

from modcli import context, __version__


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name='modcli', version=__version__)
def main():
    pass


@click.group()
def auth():
    pass


@click.command(help='Authenticate user with SSO (MOD Forum)')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
@click.option('-e', '--environment', default='labs')
def login_sso(show_token: bool, one_time: bool, environment: str):
    api_url = context.environments[environment].url

    server_host = 'localhost'
    server_port = 8099
    local_server = 'http://{0}:{1}'.format(server_host, server_port)

    class SSORequestHandler(BaseHTTPRequestHandler):
        token = ''

        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            response = self.handle_http(200)
            SSORequestHandler.token = '123'
            self.wfile.write(response)

        def handle_http(self, status_code):
            self.send_response(status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            content = '''
            <html><head><title>Success</title></head>
            <body>Authentication successful!</body></html>
            '''
            return bytes(content, 'UTF-8')

    httpd = HTTPServer((server_host, server_port), SSORequestHandler)
    httpd.timeout = 60

    webbrowser.open('{0}/users/tokens_sso?local_url={1}'.format(api_url, local_server))

    try:
        httpd.handle_request()
    except KeyboardInterrupt:
        pass

    token = SSORequestHandler.token
    _, payload, _ = token.split('.')
    username = payload['user_id']

    if not one_time:
        context.set_token(environment, username, token)
        context.set_active_env(environment)

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(crayons.green('You\'re now logged in as [{0}] in [{1}].'.format(username, environment)))


@click.command(help='Authenticate user')
@click.option('-u', '--username', type=str, prompt=True, help='User ID')
@click.option('-p', '--password', type=str, prompt=True, hide_input=True, help='User password')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
@click.option('-e', '--environment', default='labs')
def login(username: str, password: str, show_token: bool, one_time: bool, environment: str):
    api_url = context.environments[environment].url
    result = requests.post('{0}/users/tokens'.format(api_url), json={
        'user_id': username,
        'password': password,
        'agent': 'modcli:{0}'.format(__version__),
    })
    if result.status_code != 200:
        click.echo(crayons.red('Error: {0}'.format(result.json()['error-message'])), err=True)
        exit(1)
    token = result.json()['message'].strip()

    if not one_time:
        context.set_token(environment, username, token)
        context.set_active_env(environment)

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(crayons.green('You\'re now logged in as [{0}] in [{1}].'.format(username, environment)))


@click.command(help='Show current active access JWT token')
def active_token():
    token = context.active_token()
    if not token:
        click.echo(crayons.red('You must authenticate first.'), err=True)
        click.echo('Try:\n $ modcli auth login')
        exit(1)
    click.echo(token)


auth.add_command(login)
auth.add_command(login_sso)
main.add_command(active_token)
main.add_command(auth)


if __name__ == '__main__':
    main()
