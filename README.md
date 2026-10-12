# mod-devel-cli

## Installation

Using pip:

    pip install --upgrade pip
    pip install git+https://github.com/mod-audio/mod-devel-cli

Using uv:

    uv tool install git+https://github.com/mod-audio/mod-devel-cli

## Usage

```
Usage: modcli [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  auth            Authentication commands
  bundle          LV2 bundle commands
  config          Configuration commands
```

## Development

```
uv sync                                # install with the dev group (pylint, pytest)
uv run pytest                          # run the tests
uv run pylint --errors-only modcli     # lint
```

## Authentication

```
modcli auth login              # username and password
modcli auth login-forum        # MOD Forum account (login-sso still works)
modcli auth login-google       # Google account
modcli auth login-magiclink    # sign-in link sent by email
```

`login-forum` and `login-google` open the browser, and `login-magiclink` emails a sign-in link. Once you sign in, the browser hands the token back to the CLI automatically. When the browser runs on another machine (e.g. the CLI runs over SSH), paste the token the browser shows into the terminal instead.
