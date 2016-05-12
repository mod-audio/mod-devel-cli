import argparse
import base64
import json
import os
import sys
from urllib import request

from modcli import settings, crypt, get_agent_info


def encrypt_and_encode(public_key: str, data: str):
    with open(public_key, 'r') as fh:
        server_key_text = fh.read()
    encrypted = crypt.encrypt(server_key_text, data)
    return base64.encodebytes(encrypted)


def decode_and_decrypt(private_key: str, data: str):
    with open(private_key, 'r') as fh:
        device_key_text = fh.read()
    encrypted = base64.decodebytes(data.encode())
    return crypt.decrypt(device_key_text, encrypted)


def get_token(user_data: dict):
    req = request.urlopen('{0}/users/nonce'.format(settings.API_BASE_URL))
    nonce = json.loads(req.read().decode())['nonce']
    data = {
        'nonce': nonce,
        'agent': get_agent_info(),
    }
    data.update(user_data)
    message = json.dumps({'message': encrypt_and_encode(settings.API_KEY_PATH, json.dumps(data)).decode()})
    req = request.urlopen('{0}/users/tokens'.format(settings.API_BASE_URL), message.encode())
    token_message = req.read().decode()
    return json.loads(token_message)['message']


def get_token_password(user_id, password):
    return get_token({'user_id': user_id, 'password': password})


def main():
    parser = argparse.ArgumentParser(description='Retrieves access token from mod-api')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ssh-key', help='Uses ssh key .pem file instead of a password', action='store_true')
    group.add_argument('--password', help='User password')
    parser.add_argument('--ssh-key-file', help='A ssh key .pem file (default: ~/.ssh/id_rsa)')
    parser.add_argument('user_id', help='The user id')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    args = parser.parse_args()

    if args.password:
        token = get_token_password(args.user_id, args.password)
    else:
        if args.ssh_key and not args.ssh_key_file:
            args.ssh_key_file = '~/.ssh/id_rsa'
        token = decode_and_decrypt(os.path.expanduser(args.ssh_key_file), get_token({'user_id': args.user_id}))

    print(token)
    exit(0)


if __name__ == '__main__':
    main()
