import click
import crayons

from modcli import context, auth, __version__, bundle

_sso_disclaimer = '''SSO login requires you have a valid account in MOD Forum (https://forum.moddevices.com).
If your browser has an active session the credentials will be used for this login. Confirm?'''


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name='modcli', version=__version__)
def main():
    pass


@click.group(name='auth', help='Authentication commands')
def auth_group():
    pass


@click.group(name='bundle', help='LV2 bundle commands')
def bundle_group():
    pass


@click.command(help='Authenticate user with SSO (MOD Forum)')
@click.option('-s', '--show-token', type=bool, help='Print the JWT token obtained', is_flag=True)
@click.option('-o', '--one-time', type=bool, help='Only print token once (do not store it)', is_flag=True)
@click.option('-y', '--confirm-all', type=bool, help='Confirm all operations', is_flag=True)
@click.option('-d', '--dettached-mode', type=bool, help='Run process without opening a local browser', is_flag=True)
def login_sso(show_token: bool, one_time: bool, confirm_all: bool, dettached_mode: bool):
    env = context.current_env()
    if not confirm_all:
        response = click.confirm(_sso_disclaimer)
        if not response:
            exit(1)
    click.echo('Logging in to [{0}]...'.format(env.name))

    try:
        if dettached_mode:
            token = auth.login_sso_dettached(env.api_url)
        else:
            token = auth.login_sso(env.api_url)
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
        token = auth.login(username, password, env.api_url)
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


@click.command(help='Remove all tokens and reset context data')
def clear_context():
    try:
        context.clear()
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return
    click.echo(crayons.green('Context cleared'))


@click.command(help='Show current active access JWT token')
def active_token():
    token = context.active_token()
    if not token:
        click.echo(crayons.red('You must authenticate first.'), err=True)
        click.echo('Try:\n $ modcli auth login')
        exit(1)
        return

    click.echo(token)


@click.command(help='Set active environment, where ENV_NAME is the name')
@click.argument('env_name')
def set_active_env(env_name: str):
    try:
        context.set_active_env(env_name)
        context.save()
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    click.echo(crayons.green('Current environment set to: {0}'.format(env_name)))


@click.command(help='Add new environment, where ENV_NAME is the name, API_URL '
                    'and BUNDLE_URL are the API entry points')
@click.argument('env_name')
@click.argument('api_url')
@click.argument('bundle_url')
def add_env(env_name: str, api_url: str, bundle_url: str):
    try:
        context.add_env(env_name, api_url, bundle_url)
        context.set_active_env(env_name)
        context.save()
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return

    click.echo(crayons.green('Environment [{0}] added and set as active'.format(env_name)))


@click.command(help='Display context status')
def status():
    env = context.current_env()
    click.echo('Active environment: {0}'.format(env.name))
    click.echo('Authenticated in [{0}]: {1}'.format(env.name, 'Yes' if env.token else 'False'))
    click.echo('Registered environments: {0}'.format(list(context.environments.keys())))


@click.command(help='Publish LV2 bundles, where PROJECT_FILE points to the buildroot project descriptor file (JSON)')
@click.argument('project_file')
@click.option('-p', '--packages_path', type=str, help='Path to buildroot package')
def publish(project_file: str, packages_path: str):
    try:
        env = context.current_env()
        bundle.publish(project_file, packages_path, env.bundle_url)
    except Exception as ex:
        click.echo(crayons.red(str(ex)), err=True)
        exit(1)
        return


auth_group.add_command(active_token)
auth_group.add_command(login)
auth_group.add_command(login_sso)
bundle_group.add_command(publish)
main.add_command(auth_group)
main.add_command(bundle_group)
main.add_command(add_env)
main.add_command(set_active_env)
main.add_command(status)
main.add_command(clear_context)


if __name__ == '__main__':
    main()
