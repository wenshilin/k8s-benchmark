import json


def read_json_file(filename):
    with open(filename, "r") as fp:
        data = json.load(fp)
        return data
