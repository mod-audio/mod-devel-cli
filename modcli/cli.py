import click
import crayons

from modcli import context, auth, __version__


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name='modcli', version=__version__)
def main():
    pass


@click.group(name='auth', help='Authentication')
def auth_group():
    pass


@click.command(help='Authenticate user with SSO (MOD Forum)')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
def login_sso(show_token: bool, one_time: bool):
    env = context.current_env()
    click.echo('Logging in to [{0}]...'.format(env.name))

    try:
        token = auth.login_sso(env.url)
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    if not one_time:
        env.set_token(token)
        context.save()

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(crayons.green('You\'re now logged in as [{0}] in [{1}].'.format(env.username, env.name)))


@click.command(help='Authenticate user')
@click.option('-u', '--username', type=str, prompt=True, help='User ID')
@click.option('-p', '--password', type=str, prompt=True, hide_input=True, help='User password')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
def login(username: str, password: str, show_token: bool, one_time: bool):
    env = context.current_env()
    click.echo('Logging in to [{0}]...'.format(env.name))
    try:
        token = auth.login(username, password, env.url)
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    if not one_time:
        env.set_token(token)
        context.save()

    if show_token or one_time:
        print(token.strip())
    else:
        click.echo(crayons.green('You\'re now logged in as [{0}] in [{1}].'.format(username, env.name)))


@click.command(help='Show current active access JWT token')
def active_token():
    token = context.active_token()
    if not token:
        click.echo(crayons.red('You must authenticate first.'), err=True)
        click.echo('Try:\n $ modcli auth login')
        exit(1)
        return

    click.echo(token)


@click.command(help='Set active environment')
@click.argument('environment')
def set_active_env(environment: str):
    try:
        context.set_active_env(environment)
        context.save()
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    click.echo(crayons.green('Current environment set to: {0}'.format(environment)))


@click.command(help='Add new environment')
@click.argument('name')
@click.argument('url')
def add_env(name: str, url: str):
    try:
        context.add_env(name, url)
        context.set_active_env(name)
        context.save()
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    click.echo(crayons.green('Environment [{0}] added and set as active'.format(name)))


@click.command(help='Display context status')
def status():
    env = context.current_env()
    click.echo('Active environment: {0}'.format(env.name))
    click.echo('Authenticated in [{0}]: {1}'.format(env.name, 'Yes' if env.token else 'False'))
    click.echo('Registered environments: {0}'.format(list(context.environments.keys())))


auth_group.add_command(login)
auth_group.add_command(login_sso)
main.add_command(add_env)
main.add_command(active_token)
main.add_command(auth_group)
main.add_command(set_active_env)
main.add_command(status)


if __name__ == '__main__':
    main()
