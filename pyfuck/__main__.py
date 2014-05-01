#!/usr/bin/env python3


import argparse
import sys


def run(args):
    pass


def convert(args):
    pass


# common parser ====================================
parser_common = argparse.ArgumentParser(add_help=False)
parser_common.add_argument(
    "-t", "--type",
    choices=["auto", "brainfuck", "braincopter", "brainloller"],
    default="auto",
    help="Source type (default: auto).")
parser_common.add_argument(
    "source",
    type=argparse.FileType(),
    nargs="?",
    default=sys.stdin,
    help="Source file to interpret (default: sys.stdin).")
# parser_common.add_argument(
#     "-v", "--verbose",
#     action="count",
#     dest="verbosity",
#     default=0,
#     help="increase verbosity (-v, -vv, ...)")


# main parser ====================================
parser_main = argparse.ArgumentParser(prog="pyfuck", description="Interpreter and converter for Brainfuck, Brainloller and Braincopter scripts.")
actions = parser_main.add_subparsers(title="actions", help="Available actions.")


# run subparser ====================================
parser_run = actions.add_parser("run", parents=[parser_common], description="Runs a script.")
parser_run.set_defaults(func=run)


# conversion subparser ====================================
parser_conversion = actions.add_parser("convert", parents=[parser_common], description="Converts one format to another.")
parser_conversion.set_defaults(func=convert)
parser_conversion.add_argument(
    "-o", "--output",
    choices=["brainfuck", "braincopter", "brainloller"],
    required=True,
    help="Output type.")
parser_conversion.add_argument(
    "destination",
    type=argparse.FileType("w"),
    nargs="?",
    default=sys.stdout,
    help="Destination filename (default: sys.stdout).")


# MAIN ==================================================================================================
if len(sys.argv) == 1:
    parser_main.parse_args(["-h"])

args = parser_main.parse_args()
args.func(args)