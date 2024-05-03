import os
import json
from argparse import ArgumentParser

from .utilities import getkeyvalue

def construct_parser():
    parser = ArgumentParser()
    parser.add_argument("--scores-dir", dest="scores_dir", required=True, help="directory containing scores json files")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = construct_parser()