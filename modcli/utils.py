import json
import os


def read_json_file(path: str):
    if not os.path.isfile(path):
        return {}
    with open(path, 'r') as file:
        contents = file.read()
    return json.loads(contents)
