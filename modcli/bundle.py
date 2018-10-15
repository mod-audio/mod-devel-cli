import os
import shutil
import subprocess
import tempfile
from hashlib import md5

import click
import crayons
import requests

from modcli import context
from modcli.utils import read_json_file


def publish(project_file: str, packages_path: str, bundle_url: str, keep_environment: bool=False, bundles: list=None):
    token = context.active_token()
    if not token:
        raise Exception('You must authenticate first')

    if not os.path.isfile(project_file):
        raise Exception('File {0} not found or not a valid file'.format(project_file))

    if packages_path:
        if not os.path.isdir(packages_path):
            raise Exception('Packages path {0} not found'.format(packages_path))
    else:
        packages_path = os.path.dirname(project_file)

    process = read_json_file(project_file)

    # setting up process data
    if keep_environment:
        process['keep_environment'] = True
    buildroot_pkg = process.pop('buildroot_pkg', None)
    if not buildroot_pkg:
        raise Exception('Missing buildroot_pkg in project file')
    if bundles:
        process['bundles'] = [b for b in process['bundles'] if b['name'] in bundles]
        if not process['bundles']:
            raise Exception('Could not match any bundle from: {0}'.format(bundles))

    # find buildroot_pkg under packages_path
    pkg_path = next((i for i in os.walk(packages_path) if buildroot_pkg in i[1]), None)
    if not pkg_path:
        raise Exception('Could not find package {0} in {1}'.format(buildroot_pkg, packages_path))

    work_dir = tempfile.mkdtemp()
    try:
        package = '{0}.tar.gz'.format(buildroot_pkg)
        source_path = os.path.join(work_dir, package)
        try:
            subprocess.check_output(
                ['tar', 'zhcf', source_path, buildroot_pkg], stderr=subprocess.STDOUT, cwd=os.path.join(pkg_path[0])
            )
        except subprocess.CalledProcessError as ex:
            raise Exception(ex.output.decode())

        click.echo('Submitting release process for project {0} using file {1}'.format(project_file, package))
        click.echo('URL: {0}'.format(bundle_url))

        headers = {'Authorization': 'MOD {0}'.format(token)}

        result = requests.post('{0}/'.format(bundle_url), json=process, headers=headers)
        if result.status_code != 200:
            raise Exception('Error: {0}'.format(result.text))
        release_process = result.json()

        click.echo('Release process created: {0}'.format(release_process['id']))
        click.echo('Uploading buildroot package {0} ...'.format(package))
        with open(source_path, 'rb') as fh:
            data = fh.read()
        headers = {'Content-Type': 'application/octet-stream'}
        result = requests.post(release_process['source-href'], data=data, headers=headers)
        if result.status_code != 201:
            raise Exception('Error: {0}'.format(result.text))
        checksum = result.text.lstrip('"').rstrip('"')

        result_checksum = md5(data).hexdigest()
        if checksum == result_checksum:
            click.echo('Checksum match ok!')
        else:
            raise Exception('Checksum mismatch: {0} <> {1}'.format(checksum, result_checksum))
    finally:
        click.echo('Cleaning up ...')
        shutil.rmtree(work_dir, ignore_errors=True)

    release_process_url = release_process['href']
    click.echo('Retrieving release process from {0} ...'.format(release_process_url))
    release_process_full = requests.get('{0}?pretty=true'.format(release_process_url)).text
    click.echo(crayons.green('Done'))
    click.echo(crayons.blue('================ Release Process {0} ================'.format(release_process['id'])))
    click.echo(release_process_full)
    click.echo(crayons.blue('================ End Release Process ================'))
