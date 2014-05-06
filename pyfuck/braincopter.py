#!/usr/bin/env python3



import logging
import itertools

from pyfuck.png import PNG
from pyfuck.brainloller import Brainloller



class Braincopter(object):
    """
    Extends Brainloller interpreter to Braincopter.
    
    Author:
        Tomas Bedrich

    See:
        http://esolangs.org/wiki/Braincopter
    """


    COMMANDS = [
        (255, 0, 0), # ">" = red
        (128, 0, 0), # "<" = darkred
        (0, 255, 0), # "+" = green
        (0, 128, 0), # "-" = darkgreen
        (0, 0, 255), # "." = blue
        (0, 0, 128), # "," = darkblue
        (255, 255, 0), # "[" = yellow
        (128, 128, 0), # "]" = darkyellow
        (0, 255, 255), # "R" = cyan
        (0, 128, 128), # "L" = darkcyan
        (0, 0, 0) # "X" = any other
    ]

    # for reverse lookup (indexes are important)
    COMMANDS_REVERSE = [">", "<", "+", "-", ".", ",", "[", "]", "R", "L", None]
    COMMANDS_REVERSE_LEN = len(COMMANDS_REVERSE)

    def __init__(self):
        super(Braincopter, self).__init__()
        self.brainloller = Brainloller()


    def to_brainfuck(self, image):
        """
        Converts Braincopter to Brainfuck.

        Args:
            image: An image containing the Braincopter program.

        Raises:
            AttributeError, EOFError, ValueError

        Returns:
            A Brainfuck program

        Examples:
            # TODO
        """
        if not isinstance(image, PNG):
            raise AttributeError("Image is not an instance of pyfuck.png.PNG.")

        newPixels = [[self.COMMANDS[(-2 * r + 3 * g + b) % 11] for r, g, b in row] for row in image.pixels]
        image.pixels = newPixels

        return self.brainloller.to_brainfuck(image)


    def to_braincopter(self, program, image):
        """
        Does minor colour changes in image to encode given Brainfuck program.

        Args:
            program: A Brainfuck program to encode.
            image: An image to change.

        Returns:
            The image (the image argument).

        Examples:
            # TODO maybe?
        """

        def commands():
            width = len(image.pixels) - 1
            way_right = True
            i = 0
            for command in program:
                # borders
                if i == width:
                    if way_right:
                        yield "R"
                        yield "R"
                    else:
                        yield "L"
                        yield "L"
                    way_right = not way_right
                    i = 1

                # commands
                yield command
                i += 1

            # nop
            while True:
                yield None

        command = commands()

        # FIXME performance (maybe)
        newPixels = [[self._find_similar(next(command), pixel) for pixel in (reversed(row) if i % 2 else row)] for i, row in enumerate(image.pixels)]
        newPixels = [list(reversed(row)) if i % 2 else row for i, row in enumerate(newPixels)]
        image.pixels = newPixels

        if next(command):
            raise IOError("Image is too small to encode whole program.")

        return image


    @classmethod
    def _find_similar(cls, command, pixel):
        """
        Returns a similar colour according to desired command.

        Examples:
            >>> Braincopter._find_similar("+", (0, 0, 0))
            (0, 0, 2)
            >>> Braincopter._find_similar(None, (0, 0, 0))
            (0, 0, 10)
            >>> Braincopter._find_similar("+", (255, 255, 255))
            (255, 255, 253)
            >>> Braincopter._find_similar("L", (255, 255, 253))
            (255, 255, 249)
        """
        r, g, b = pixel
        b += cls.COMMANDS_REVERSE.index(command) - (-2 * r + 3 * g + b) % 11
        if b > 255:
            b -= cls.COMMANDS_REVERSE_LEN
        elif b < 0:
            b += cls.COMMANDS_REVERSE_LEN
        return (r, g, b)



if __name__ == '__main__':
    print("This file is not meant to be executed directly. Please use it as a module instead.")
