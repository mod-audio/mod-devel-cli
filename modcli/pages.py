from importlib.resources import files
from string import Template

_sign_in = Template(files('modcli').joinpath('sign_in.html').read_text(encoding='utf-8'))


def signed_in() -> bytes:
    return _render('#10B981', 'You\'re signed in', 'Return to the terminal. This window can be closed.')


def sign_in_failed() -> bytes:
    return _render('#FF3B30', 'Sign-in failed', 'Invalid authentication response.')


def _render(color: str, title: str, message: str) -> bytes:
    return _sign_in.substitute(color=color, title=title, message=message).encode('utf-8')
