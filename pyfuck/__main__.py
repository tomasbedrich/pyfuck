#!/usr/bin/env python3



import argparse
import sys
import logging

from pyfuck.png import PNG, ValidationException
from pyfuck.brainfuck import Brainfuck
from pyfuck.brainloller import Brainloller
from pyfuck.braincopter import Braincopter



class Interpreter(object):


    # for determining image type: braincopter / brainloller
    _THRESHOLD = 0.8 # percent


    def __init__(self, args):
        self.type = args.type
        self.image = None
        self.contents = None
        self.source = args.source

        # normalize source
        if self.source.name == "<stdin>":
            self.source = open(sys.stdin.fileno(), "rb")

        # decetect source type and load an image
        if self.type == "auto":
            self.type = self.guess_type(self.source)

        # type manually set or plaing brainfuck => load either contents or image
        if self.type == "brainfuck":
            try:
                self.source.seek(0)
                with self.source as f:
                    self.contents = f.read().decode()
            except UnicodeDecodeError as e:
                logging.error("Unable to read file '{}': {}".format(self.source.name, e))

        elif not self.image:
            self.image = PNG().load(self.source)


    def guess_type(self, target):
        try:
            self.image = PNG().load(target)

            i = 0
            score = 0
            stop = len(self.image.pixels) * self._THRESHOLD
            for y, row in enumerate(self.image.pixels):
                for pixel in row:
                    i += 1
                    if pixel in Brainloller.COMMANDS:
                        score += 1
                if y > stop:
                    break

            if (i * self._THRESHOLD) < score:
                res, msg = "brainloller", "probability {:.1f}%".format(100 * i / score)
            else:
                res, msg = "braincopter", "fallback"

        except ValidationException:
            res, msg = "brainfuck", "not a valid PNG"

        logging.info("Detected source type: {} ({}).".format(res, msg))
        return res


    def run(self):
        if not self.contents and not self.image:
            return

        logging.info("Running source file '{}' of type {}.".format(self.source.name, self.type))

        if self.type == "brainfuck":
            Brainfuck().eval(self.contents)

        elif self.type == "brainloller":
            Brainloller().eval(self.image)

        elif self.type == "braincopter":
            Braincopter().eval(self.image)


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
    type=argparse.FileType("rb"),
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
parser_run.set_defaults(func="run")


# conversion subparser ====================================
parser_conversion = actions.add_parser("convert", parents=[parser_common], description="Converts one format to another.")
parser_conversion.set_defaults(func="convert")
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
if __name__ == '__main__':
    if len(sys.argv) > 1:
        logging.basicConfig(level=logging.INFO)
        args = parser_main.parse_args()
        interpreter = Interpreter(args)
        getattr(interpreter, args.func)()
    else:
        parser_main.parse_args(["-h"])
