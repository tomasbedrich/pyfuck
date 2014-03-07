#!/usr/bin/env python3



import logging
from collections import namedtuple

from pyfuck.png import PNG



class Command(object):
    """
    Holds one Brainloller command.

    Author:
        Tomas Bedrich
    """


    def __init__(self, color, command):
        super(Command, self).__init__()
        self.color = color
        self.command = command


    def __eq__(self, other):
        return isinstance(Command, other) and self.color == other.color and self.command == other.command



class Brainloller(object):
    """
    Extends Brainfuck! interpreter to Brainloller.
    
    Author:
        Tomas Bedrich

    See:
        http://esolangs.org/wiki/Brainloller
    """


    COMMANDS = (
        Command((255, 0, 0), ">"), # red
        Command((128, 0, 0), "<"), # darkred
        Command((0, 255, 0), "+"), # green
        Command((0, 128, 0), "-"), # darkgreen
        Command((0, 0, 255), "."), # blue
        Command((0, 0, 128), ","), # darkblue
        Command((255, 255, 0), "["), # yellow
        Command((128, 128, 0), "]"), # darkyellow
        Command((0, 255, 255), "R"), # cyan
        Command((0, 128, 128), "L") # darkcyan
    )


    def __init__(self):
        super(Brainloller, self).__init__()


    def eval(self, image, stdout=None, stdin=None):
        """
        Evaluates the Brainloller program stored in image.

        Args:
            image: An image containing the Brainloller program.
            stdout: Output destination. Passed to print() function. Default is sys.stdout.
            stdin: Input source. Any iterator returning individual chars can be passed. Default is sys.stdin.

        Examples:
            # TODO
        """
        pass



def main():
    logging.basicConfig(level=logging.INFO)
    # TODO



if __name__ == '__main__':
    main()
