#!/usr/bin/env python3


import logging

from pyfuck.png import PNG
from pyfuck.brainfuck import Brainfuck


class Brainloller(object):

    """
    Extends Brainfuck! interpreter to Brainloller.

    Author:
        Tomas Bedrich

    See:
        http://esolangs.org/wiki/Brainloller
    """

    COMMANDS = {
        (255, 0, 0): ">",  # red
        (128, 0, 0): "<",  # darkred
        (0, 255, 0): "+",  # green
        (0, 128, 0): "-",  # darkgreen
        (0, 0, 255): ".",  # blue
        (0, 0, 128): ",",  # darkblue
        (255, 255, 0): "[",  # yellow
        (128, 128, 0): "]",  # darkyellow
        (0, 255, 255): "R",  # cyan
        (0, 128, 128): "L"  # darkcyan
    }

    COMMANDS_REVERSE = dict(zip(COMMANDS.values(), COMMANDS.keys()))
    COMMANDS_REVERSE.pop("R")
    COMMANDS_REVERSE.pop("L")

    def __init__(self):
        super(Brainloller, self).__init__()
        self.brainfuck = Brainfuck()

    def to_brainfuck(self, image):
        """
        Converts Brainloller to Brainfuck.

        Args:
            image: An image containing the Brainloller program.

        Raises:
            AttributeError, EOFError, ValueError

        Returns:
            A Brainfuck program

        Examples:
            >>> image = PNG().load("test/assets/hello_world.brainloller.png")
            >>> program = Brainloller().to_brainfuck(image)
            >>> Brainfuck().eval(program)
            Hello World!
        """

        if not isinstance(image, PNG):
            raise AttributeError("Image is not an instance of pyfuck.png.PNG.")

        program = []

        pcX = 0  # = program counter X
        pcY = 0  # = program counter Y
        NORTH, EAST, SOUTH, WEST = range(4)
        way = EAST  # program counter way

        while (0 <= pcX < image.header.width) and (0 <= pcY < image.header.height):

            colour = image.pixels[pcY][pcX]
            command = self.COMMANDS.get(colour)

            logging.debug("Processing pixel at [{},{}], colour {} - command: {}".format(pcX, pcY, colour, command))

            # rotate right
            if command is "R":
                way = (way + 1) % 4

            # rotate left
            elif command is "L":
                way = (way - 1) % 4

            # command
            elif command is not None:
                program.append(command)

            # program counter depends on the way
            if way == EAST:
                pcX += 1
            elif way == SOUTH:
                pcY += 1
            elif way == WEST:
                pcX -= 1
            else:
                pcY -= 1

        return "".join(program)

    def to_brainloller(self, program):
        """
        Converts Brainfuck to Brainloller.

        Args:
            program: A Brainfuck program to encode.

        Returns:
            A PNG object containing Brainloller image.

        Examples:
            >>> image = Brainloller().to_brainloller(".")
            >>> print(image.header) #doctest: +ELLIPSIS
            <pyfuck.png.IHDR ...
            width: 1
            height: 1
            ...
        """
        res = []

        for command in program:
            try:
                res.append(self.COMMANDS_REVERSE[command])
            except KeyError:
                # unknown characters are comments in Brainfuck
                continue

        image = PNG()
        image.pixels = [res]
        return image


if __name__ == '__main__':
    print("This file is not meant to be executed directly. Please use it as a module instead.")
