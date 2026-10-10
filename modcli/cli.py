import secrets
import sys
import webbrowser

import click
from importlib.metadata import version

from modcli import context, auth, bundle, token_receiver

# seconds to wait for the token, per browser login
_SSO_TIMEOUT = 5 * 60
_GOOGLE_TIMEOUT = 5 * 60
_MAGICLINK_TIMEOUT = 15 * 60

# -y no longer does anything; kept so existing scripts passing it keep working
_ignored_confirm_all = click.option('-y', '--confirm-all', is_flag=True, hidden=True, expose_value=False)


def _normalize_command_name(name):
    return name.replace('_', '-')


@click.group(context_settings=dict(
    help_option_names=['-h', '--help'],
    token_normalize_func=_normalize_command_name
))


@click.version_option(prog_name='modcli', version=version('mod-devel-cli'))
def main():
    pass


@click.group(name='auth', help='Authentication commands')
def auth_group():
    pass


@click.group(name='bundle', help='LV2 bundle commands')
def bundle_group():
    pass


@click.group(name='config', help='Configuration commands')
def config_group():
    pass


def _open_browser(url: str):
    click.echo('Sign in in the browser. If it doesn\'t open, visit:')
    click.echo(url)
    webbrowser.open(url)


def _start_sso(api_url: str, local_url: str):
    click.echo('Sign in with your MOD Forum account (https://forum.mod.audio); an existing browser session is used.')
    _open_browser(auth.sso_url(api_url, local_url))
    # Discourse redirects without a state
    return None


def _start_google(api_url: str, local_url: str):
    state = secrets.token_urlsafe(16)
    _open_browser(auth.google_url(api_url, local_url, state))
    return state


def _start_magiclink(email: str):
    def start(api_url: str, local_url: str):
        state = secrets.token_urlsafe(16)
        auth.send_magic_link(api_url, email, local_url, state)
        click.echo(f'A sign-in link was sent to {email}. Open it and confirm.')
        click.echo('No email? Only one link is sent per minute, so wait a minute before trying again.')
        return state
    return start


def _receive_token(api_url: str, timeout: int, start):
    port = token_receiver.get_open_port()
    state = start(api_url, token_receiver.local_url(port))
    click.echo('If the browser can\'t reach this machine, paste the token it shows and press ENTER: ', nl=False)
    token, source = token_receiver.receive_token(port, timeout, state)
    if source != 'paste':
        click.echo()
    if not token:
        raise Exception('Authentication failed!')
    return token


def _browser_login(env_name: str, show_token: bool, one_time: bool, timeout: int, start):
    if env_name:
        context.set_active_env(env_name)
    env = context.current_env()
    if not one_time:
        click.echo(f'Logging in to [{env.name}]...')

    try:
        token = _receive_token(env.api_url, timeout, start)
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return

    if not one_time:
        env.set_token(token)
        context.save()

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(click.style(f'You\'re now logged in as [{env.username}] in [{env.name}].', fg='green'))


def _browser_login_options(command):
    options = [
        click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True),
        click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True),
        click.option('-e', '--env-name', type=str, help='Switch to environment before authenticating'),
        _ignored_confirm_all,
    ]
    for option in reversed(options):
        command = option(command)
    return command


@click.command(help='Authenticate user with SSO (MOD Forum)')
@_browser_login_options
def login_sso(show_token: bool, one_time: bool, env_name: str):
    _browser_login(env_name, show_token, one_time, _SSO_TIMEOUT, _start_sso)


@click.command(help='Authenticate user with Google')
@_browser_login_options
def login_google(show_token: bool, one_time: bool, env_name: str):
    _browser_login(env_name, show_token, one_time, _GOOGLE_TIMEOUT, _start_google)


@click.command(help='Authenticate user with a sign-in link sent by email')
@click.option('--email', type=str, prompt=True, help='Email address of the user')
@_browser_login_options
def login_magiclink(email: str, show_token: bool, one_time: bool, env_name: str):
    _browser_login(env_name, show_token, one_time, _MAGICLINK_TIMEOUT, _start_magiclink(email))


@click.command(help='Authenticate user')
@click.option('-u', '--username', type=str, prompt=True, help='User ID')
@click.option('-p', '--password', type=str, prompt=True, hide_input=True, help='User password')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
@click.option('-e', '--env-name', type=str, help='Switch to environment before authenticating')
@_ignored_confirm_all
def login(username: str, password: str, show_token: bool, one_time: bool, env_name: str):
    if env_name:
        context.set_active_env(env_name)
    env = context.current_env()
    if not one_time:
        click.echo(f'Logging in to [{env.name}]...')
    try:
        token = auth.login(username, password, env.api_url)
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return

    if not one_time:
        env.set_token(token)
        context.save()

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(click.style(f'You\'re now logged in as [{username}] in [{env.name}].', fg='green'))


@click.command(help='Remove all tokens and reset context data')
def clear_context():
    try:
        context.clear()
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return
    click.echo(click.style('Context cleared', fg='green'))


@click.command(help='Show current active access JWT token')
@click.option('-e', '--env-name', type=str, help='Show current active token from a specific environment')
def active_token(env_name: str):
    if env_name:
        context.set_active_env(env_name)
    token = context.active_token()
    if not token:
        click.echo(click.style('You must authenticate first.', fg='red'), err=True)
        click.echo('Try:\n $ modcli auth login')
        sys.exit(1)
        return

    click.echo(token)


@click.command(help='Set active environment, where ENV_NAME is the name')
@click.argument('env-name')
def set_active_env(env_name: str):
    try:
        context.set_active_env(env_name)
        context.save()
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return

    click.echo(click.style(f'Current environment set to: {env_name}', fg='green'))


@click.command(help='Add new environment, where ENV_NAME is the name, API_URL '
                    'and BUNDLE_URL are the API entry points')
@click.argument('env-name')
@click.argument('api-url')
@click.argument('bundle-url')
def add_env(env_name: str, api_url: str, bundle_url: str):
    try:
        context.add_env(env_name, api_url, bundle_url)
        context.set_active_env(env_name)
        context.save()
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return

    click.echo(click.style(f'Environment [{env_name}] added and set as active', fg='green'))


@click.command(help='List current configuration', name='list')
def list_config():
    env = context.current_env()
    click.echo(f'Active environment: {env.name}')
    click.echo(f'Authenticated in [{env.name}]: {"Yes" if env.token else "No"}')
    click.echo(f'Registered environments: {list(context.environments.keys())}')


@click.command(help='Publish LV2 bundles, where PROJECT_FILE points to the buildroot project descriptor file (JSON)')
@click.argument('project_file')
@click.option('-p', '--packages-path', type=str, help='Path to buildroot package')
@click.option('-s', '--show-result', type=bool, help='Print pipeline process result', is_flag=True)
@click.option('-k', '--keep-environment', type=bool, help='Don\'t remove build environment after build', is_flag=True)
@click.option('-r', '--rebuild', type=bool, help='Don\'t increment release number, just rebuild', is_flag=True)
@click.option('-e', '--env', type=str, help='Environment where the bundles will be published')
@click.option('-f', '--force', type=bool, help='Don\'t ask for confirmation', is_flag=True)
def publish(project_file: str, packages_path: str, show_result: bool, keep_environment: bool,
            rebuild: bool, env: str, force: bool):
    try:
        bundle.publish(project_file, packages_path, show_result=show_result,
                       keep_environment=keep_environment, rebuild=rebuild, env_name=env, force=force)
    except Exception as ex:
        click.echo(click.style(str(ex), fg='red'), err=True)
        sys.exit(1)
        return


auth_group.add_command(active_token)
auth_group.add_command(login)
auth_group.add_command(login_sso)
auth_group.add_command(login_google)
auth_group.add_command(login_magiclink)
bundle_group.add_command(publish)
config_group.add_command(add_env)
config_group.add_command(set_active_env)
config_group.add_command(list_config)
config_group.add_command(clear_context)
main.add_command(auth_group)
main.add_command(bundle_group)
main.add_command(config_group)


if __name__ == '__main__':
    main()
