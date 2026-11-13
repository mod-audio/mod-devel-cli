import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class Response:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.text = body.decode('utf-8') if isinstance(body, bytes) else body

    def json(self):
        return json.loads(self.text)


def _check_scheme(url):
    # urlopen also opens file:// and other schemes; URLs here come from the config and the server
    if not url.lower().startswith(('http://', 'https://')):
        raise Exception(f'Invalid URL: {url}')


def get(url):
    _check_scheme(url)
    try:
        with urlopen(url) as response:  # nosec B310
            return Response(response.status, response.read())
    except HTTPError as e:
        return Response(e.code, e.read())


def post(url, data=None, json_data=None, headers=None):
    _check_scheme(url)
    headers = headers or {}

    if json_data is not None:
        body = json.dumps(json_data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    elif data is not None:
        body = data
    else:
        body = None

    request = Request(url, data=body, headers=headers, method='POST')

    try:
        with urlopen(request) as response:  # nosec B310
            return Response(response.status, response.read())
    except HTTPError as e:
        return Response(e.code, e.read())
