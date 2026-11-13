import os
import shutil
import subprocess
import tempfile
from hashlib import md5

import click

from modcli import context, http
from modcli.utils import read_json_file


def publish(project_file: str, packages_path: str, keep_environment: bool=False, bundles: list=None,
            show_result: bool=False, rebuild: bool=False, env_name: str=None, force: bool=False):
    project_file = os.path.realpath(project_file)
    packages_path = os.path.realpath(packages_path) if packages_path else None

    env = context.get_env(env_name)
    if not env.token:
        raise Exception('You must authenticate first')

    if not os.path.isfile(project_file):
        raise Exception(f'File {project_file} not found or not a valid file')

    if packages_path:
        if not os.path.isdir(packages_path):
            raise Exception(f'Packages path {packages_path} not found')
    else:
        packages_path = os.path.dirname(project_file)

    project = os.path.split(project_file)[1]
    if not force and not click.confirm(f'Project {click.style(project, fg="green")} will be compiled and published in [{click.style(env.name, fg="green")}], '
                                       'do you confirm?'):
        raise Exception('Cancelled')

    process = read_json_file(project_file)

    # setting up process data
    if keep_environment:
        process['keep_environment'] = True
    process['rebuild'] = rebuild
    buildroot_pkg = process.pop('buildroot_pkg', None)
    mk_filename = f'{buildroot_pkg}.mk'
    if not buildroot_pkg:
        raise Exception('Missing buildroot_pkg in project file')
    if bundles:
        process['bundles'] = [b for b in process['bundles'] if b['name'] in bundles]
        if not process['bundles']:
            raise Exception(f'Could not match any bundle from: {bundles}')

    # find buildroot_pkg under packages_path
    mk_path = next((i[0] for i in os.walk(packages_path) if mk_filename in i[2]), None)
    if not mk_path:
        raise Exception(f'Could not find buildroot mk file for package {buildroot_pkg} in {packages_path}')
    basename = os.path.basename(mk_path)
    if basename != buildroot_pkg:
        raise Exception(f'The package folder containing the .mk file has to be named {buildroot_pkg}')
    pkg_path = os.path.dirname(mk_path)

    work_dir = tempfile.mkdtemp()
    try:
        package = f'{buildroot_pkg}.tar.gz'
        source_path = os.path.join(work_dir, package)
        try:
            subprocess.check_output(
                ['tar', 'zhcf', source_path, buildroot_pkg], stderr=subprocess.STDOUT, cwd=os.path.join(pkg_path)
            )
        except subprocess.CalledProcessError as ex:
            raise Exception(ex.output.decode()) from ex

        click.echo(f'Submitting release process for project {project_file} using file {package}')
        click.echo(f'URL: {env.bundle_url}')

        headers = {'Authorization': f'MOD {env.token}'}

        result = http.post(f'{env.bundle_url}/', json_data=process, headers=headers)
        if result.status_code == 401:
            raise Exception('Invalid token - please authenticate (see \'modcli auth\')')
        elif result.status_code != 200:
            raise Exception(f'Error: {result.text}')
        release_process = result.json()

        click.echo(f'Release process created: {release_process["id"]}')
        click.echo(f'Uploading buildroot package {package} ...')
        with open(source_path, 'rb') as fh:
            data = fh.read()
        headers = {'Content-Type': 'application/octet-stream'}
        result = http.post(release_process['source-href'], data=data, headers=headers)
        if result.status_code == 401:
            raise Exception('Invalid token - please authenticate (see \'modcli auth\')')
        elif result.status_code != 201:
            raise Exception(f'Error: {result.text}')
        checksum = result.text.lstrip('"').rstrip('"')

        result_checksum = md5(data, usedforsecurity=False).hexdigest()
        if checksum == result_checksum:
            click.echo('Checksum match ok!')
        else:
            raise Exception(f'Checksum mismatch: {checksum} <> {result_checksum}')
    finally:
        click.echo('Cleaning up...')
        shutil.rmtree(work_dir, ignore_errors=True)

    release_process_url = release_process['href']
    click.echo(click.style(f'Process url: {release_process_url}?pretty=true', fg='blue'))
    click.echo(click.style('Done', fg='green'))
    if show_result:
        click.echo(f'Retrieving release process from {release_process_url} ...')
        release_process_full = http.get(f'{release_process_url}?pretty=true').text
        click.echo(click.style(f'================ Release Process {release_process["id"]} ================', fg='blue'))
        click.echo(release_process_full)
        click.echo(click.style('================ End Release Process ================', fg='blue'))
