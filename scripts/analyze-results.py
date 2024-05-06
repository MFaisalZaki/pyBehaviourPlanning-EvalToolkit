import os
import json
from argparse import ArgumentParser

# from .utilities import getkeyvalue

def getkeyvalue(data, target_key):
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            result = getkeyvalue(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = getkeyvalue(item, target_key)
            if result is not None:
                return result
    return None

# move to utils.

def read_scores(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                if len(data) == 0: continue
                pass



def construct_parser():
    parser = ArgumentParser()
    parser.add_argument("--scores-dir", dest="scores_dir", required=True, help="directory containing scores json files")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = construct_parser()
    read_scores(args.scores_dir)
    pass