#!/usr/bin/env python3



import logging

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



def main():
    logging.basicConfig(level=logging.INFO)
    # TODO



if __name__ == '__main__':
    main()
