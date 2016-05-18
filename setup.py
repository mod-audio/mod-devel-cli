from setuptools import setup
from modcli import __version__

setup(
    name='mod-cli',
    version=__version__,
    description='MOD Command Line Interface',
    author='Alexandre Cunha',
    author_email='alex@moddevices.com',
    license='Proprietary',
    include_package_data=True,
    package_data={
        'modcli': ['mod_api_key.pub'],
    },
    packages=[
        'modcli',
    ],
    install_requires=[
        'mod-auth==1.0.0',
    ],
    dependency_links=[
    ],
    entry_points={
        'console_scripts': [
            'mod-token = modcli.token_cli:main',
            'mod-api = modcli.api_cli:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url='http://moddevices.com/',
)
