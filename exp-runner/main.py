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
    runner,
    generator
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

    for cmd in ["solve"]:
        # TODO: We will need to think about this. The best way is to pass a json file containing all the experiment details.
        pass
        # subparser[cmd].add_argument( "--planner-cfg-file", type=str, help="Planner configuration file.")
        # subparser[cmd].add_argument( "--exp-details-dir", type=str, help="Path to the directory containing all results.")

        # subparser[cmd].add_argument( "--domain",      type=str, help="Path to a domain file.")
        # subparser[cmd].add_argument( "--problem",     type=str, help="Path to a problem file.")
        
        # subparser[cmd].add_argument( "--domainname",  type=str, help="Domain name ")
        # subparser[cmd].add_argument( "--instanceno",  type=int, help="Instance number ")
        # subparser[cmd].add_argument( "--ipc-year",    type=str, help="Path to the directory containing all results.")

        # subparser[cmd].add_argument( "--run-dir")
        # subparser[cmd].add_argument( "--results-dump-dir", type=str, help="Path to a directory to dump the results.")
    
    for cmd in ["generate"]:
        subparser[cmd].add_argument( "--exp-details-dir", type=str, help="Path to the directory containing all results.")
        subparser[cmd].add_argument( "--partition", type=str, help="Sturm partition to use.")
        subparser[cmd].add_argument( "--sandbox-dir", type=str, help="Path to a sandbox directory to contain all processed files and generated plans.")
        subparser[cmd].add_argument( "--planning-tasks-dir", type=str, help="Path to the directory containing all planning tasks.")


    return parser

_COMMANDS = {
    "generate": {
        "fn": generator.generate,
        "desc": "Generate the experiments files."
    },
}

if __name__ == "__main__":
    profilecode = True
    ARG_PARSER = _create_arg_parser()    
    sys.exit(main(ARG_PARSER))