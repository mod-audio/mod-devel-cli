import click
import crayons
import requests

from modcli import settings, config, __version__


def _api_url(path: str):
    return '{0}/{1}'.format(settings.API_URL, path.lstrip('/'))


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name='modcli', version=__version__)
def main():
    pass


@click.group()
def auth():
    pass


@click.command(help='Authenticate user')
@click.option('-u', '--username', type=str, prompt=True, help='User ID')
@click.option('-p', '--password', type=str, prompt=True, hide_input=True, help='User password')
@click.option('-s', '--show_token', type=bool, help='Print the JWT token obtained', is_flag=True)
def login(username: str, password: str, show_token: bool):
    result = requests.post(_api_url('/users/tokens'), json={
        'user_id': username,
        'password': password,
        'agent': 'modcli:{0}'.format(__version__),
    })
    if result.status_code != 200:
        click.echo(crayons.red('Error: {0}'.format(result.json()['error-message'])), err=True)
        exit(1)
    token = result.json()['message'].strip()
    config.save_token(token, username)
    click.echo(crayons.green('You\'re now logged in as [{0}].'.format(username)))
    if show_token:
        click.echo('Token: {0}'.format(token))


@click.command(help='Show current active access JWT token')
def active_token():
    token = config.read_token()
    if not token:
        click.echo(crayons.red('You must authenticate first.'), err=True)
        click.echo('Try:\n $ modcli auth login')
        exit(1)
    click.echo(token)


auth.add_command(login)
auth.add_command(active_token)
main.add_command(auth)


if __name__ == '__main__':
    main()
