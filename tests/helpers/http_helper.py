from modcli.http import Response


class FakePost:
    '''Stands in for modcli.http.post: records each call and answers with `response`.'''

    def __init__(self, status_code=200, body='{"message": "the-token"}'):
        self.response = Response(status_code, body)
        self.calls = []

    def __call__(self, url, json_data=None, **_):
        self.calls.append((url, json_data))
        return self.response
