import argparse
import json
import os
import sys
from urllib import request
from urllib.error import HTTPError

from modcli import settings, token_cli

_MOD_HOME = os.path.expanduser('~/.mod')


def post(url_path: str, data: dict):
    url = '{0}{1}'.format(settings.API_BASE_URL, url_path)
    req = request.urlopen(url, json.dumps(data).encode())
    result = req.read()
    if result:
        return json.loads(result.decode())
    return result


def register(args):
    data = {
        'user_id': args.user_id,
        'name': args.name,
        'email': args.email,
        'password': args.password,
    }
    post('/users', data)
    print('User {0} registered'.format(args.user_id))
    init(args.user_id, args.password)


def init(user_id, password):
    access_token = token_cli.get_token_password(user_id, password)
    os.makedirs(_MOD_HOME, exist_ok=True)
    with open(os.path.join(_MOD_HOME, 'config'), 'w') as f:
        f.write(json.dumps({'user_id': user_id}, sort_keys=True, indent=4))
        f.write(os.linesep)
    with open(os.path.join(_MOD_HOME, 'access_token'), 'w') as f:
        f.write(access_token)
        f.write(os.linesep)


def _init(args):
    init(args.user_id, args.password)


def main():
    parser = argparse.ArgumentParser(description='Access MOD API')
    subparsers = parser.add_subparsers()
    # register
    parser_register = subparsers.add_parser('register', help='Register a new user')
    parser_register.add_argument('user_id', help='User identification (length: >5)')
    parser_register.add_argument('password', help='Password')
    parser_register.add_argument('name', help='Full name')
    parser_register.add_argument('email', help='User email address')
    parser_register.set_defaults(func=register)
    # init
    parser_init = subparsers.add_parser('init', help='Obtain a token and save')
    parser_init.add_argument('user_id', help='User identification')
    parser_init.add_argument('password', help='Password')
    parser_init.set_defaults(func=_init)

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    args = parser.parse_args()
    if hasattr(args, 'func'):
        try:
            args.func(args)
            exit(0)
        except HTTPError as e:
            print(e)
            resp = e.read()
            if resp:
                print(resp.decode())
            exit(1)
        except Exception as e:
            print(e)
            exit(1)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()
