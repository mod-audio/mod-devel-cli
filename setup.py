from setuptools import setup
from modcli import __version__

setup(
    name='mod-cli',
    version=__version__,
    description='MOD Command Line Interface',
    author='Alexandre Cunha',
    author_email='alex@moddevices.com',
    license='Proprietary',
    packages=[
        'modcli',
    ],
    install_requires=[
        'pycrypto==2.7a1',
    ],
    dependency_links=[
        'http://github.com/dlitz/pycrypto/tarball/v2.7a1#egg=pycrypto-2.7a1',
    ],
    entry_points={
        'console_scripts': [
            'mod-token = modcli.token:main',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    url='http://moddevices.com/',
)
