from importlib.metadata import version
from urllib import parse

from modcli import http


def login(username: str, password: str, api_url: str):
    result = http.post(f'{api_url}/users/tokens', json_data={
        'user_id': username,
        'password': password,
        'agent': f'modcli:{version("mod-devel-cli")}',
    })
    if result.status_code != 200:
        raise Exception(f'Error: {result.json()["error-message"]}')
    return result.json()['message'].strip()


def sso_url(api_url: str, local_url: str, state: str):
    query = parse.urlencode({'local_url': local_url, 'state': state})
    return f'{api_url}/users/tokens_sso?{query}'


def google_url(api_url: str, local_url: str, state: str):
    query = parse.urlencode({'aud': 'api', 'local_url': local_url, 'state': state})
    return f'{api_url}/users/tokens_google?{query}'


def send_magic_link(api_url: str, email: str, local_url: str, state: str):
    result = http.post(f'{api_url}/users/tokens_magiclink', json_data={
        'email': email,
        'aud': 'api',
        'local_url': local_url,
        'state': state,
    })
    if result.status_code != 200:
        raise Exception(f'Error: {result.json()["error-message"]}')
