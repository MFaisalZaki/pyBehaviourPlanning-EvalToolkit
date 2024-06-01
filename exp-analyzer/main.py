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
    analyzer
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
        description="Experiment analyzer for the behaviour space implementation.",
        epilog=cmd_list,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="command")
    subparser = {}
    for (cmd, cmd_attributes) in _COMMANDS.items():
        subparser[cmd] = subparsers.add_parser(cmd, description=cmd_attributes["desc"])
        subparser[cmd].set_defaults(func=cmd_attributes["fn"])

    for cmd in ["analyze"]:
        subparser[cmd].add_argument( "--dump-results-dir", type=str, help="Dump results directory.")
        subparser[cmd].add_argument( "--compare-different-encodings-run", action="store_true", help="Profile the code.")
        subparser[cmd].add_argument( "--output-dir", type=str, help="Processed results directory.")
    
    return parser

_COMMANDS = {
    "analyze": {
        "fn": analyzer.analyze,
        "desc": "Analyze the experiments files."
    }
}

if __name__ == "__main__":
    profilecode = True
    ARG_PARSER = _create_arg_parser()    
    sys.exit(main(ARG_PARSER))