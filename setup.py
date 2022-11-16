import re
import sys

from setuptools import setup

with open('modcli/__init__.py', 'r') as fh:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fh.read(), re.MULTILINE).group(1)

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

setup(
    name='mod-devel-cli',
    python_requires='>=3',
    version=version,
    description='MOD Command Line Interface',
    author='Alexandre Cunha',
    author_email='alex@moddevices.com',
    license='Proprietary',
    install_requires=[
        'click==6.7',
        'crayons==0.1.2',
        'requests>=2.18.4',
    ],
    packages=[
        'modcli',
    ],
    entry_points={
        'console_scripts': [
            'modcli = modcli.cli:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    url='http://moddevices.com/',
)
