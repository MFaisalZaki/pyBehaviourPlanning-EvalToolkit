"""
Program entry point for experiments on the command line.
"""

import argparse
from importlib import metadata
import os
import sys
from copy import deepcopy
import cProfile

from operations import (
    modifiers
)

def main(ARG_PARSER):
    """
    Entry point function.
    """
    args = ARG_PARSER.parse_args()
    exitcode = args.func(args)
    return 0

def _create_arg_parser():
    cmd_list = "commands:\n"
    max_cmd_length = max(len(cmd) for cmd in _COMMANDS)
    col_width = max_cmd_length + 2
    for (cmd, cmd_attributes) in _COMMANDS.items():
        cmd_list += cmd.ljust(col_width) + cmd_attributes["desc"] + "\n"
    cmd_list += "Run `main <COMMAND> --help` for command-specific help."
 
    parser = argparse.ArgumentParser(
        prog="exp",
        description="Experiment runner for the behaviour space implementation.",
        epilog=cmd_list,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="command")
    subparser = {}
    for (cmd, cmd_attributes) in _COMMANDS.items():
        subparser[cmd] = subparsers.add_parser(cmd, description=cmd_attributes["desc"])
        subparser[cmd].set_defaults(func=cmd_attributes["fn"])

    for cmd in ["replace"]:
        subparser[cmd].add_argument( "--problem-files", action="store_true", help="Problem files.")
        subparser[cmd].add_argument( "--tag", type=str, help="Tag to replace.")
        subparser[cmd].add_argument( "--value", type=str, help="Value to replace with.", default="")
        subparser[cmd].add_argument( "--dims", nargs='+', type=str, help="List of dims values.", default=[])
        subparser[cmd].add_argument( "--dir", type=str, help="Directory to search for files.", default="")
    
    for cmd in ["update-symk"]:
        subparser[cmd].add_argument( "--dir", type=str, help="Directory to search for files.", default="")
        subparser[cmd].add_argument( "--dump-dir", type=str, help="Directory to dump files.", default="")
        subparser[cmd].add_argument( "--cost-bound", type=float, help="Cost bound factor.", default=1.0)
    
    return parser

_COMMANDS = {
    "replace": {
        "fn": modifiers.replace,
        "desc": "replaces paramters in exp results."
    },
    "update-symk": {
        "fn": modifiers.update_symk_oversubscription_dims,
        "desc": "updates symk oversubscription dims."
    }
}

if __name__ == "__main__":
    profilecode = True
    ARG_PARSER = _create_arg_parser()    
    sys.exit(main(ARG_PARSER))