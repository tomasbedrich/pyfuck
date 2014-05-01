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
        (255, 0, 0): ">", # red
        (128, 0, 0): "<", # darkred
        (0, 255, 0): "+", # green
        (0, 128, 0): "-", # darkgreen
        (0, 0, 255): ".", # blue
        (0, 0, 128): ",", # darkblue
        (255, 255, 0): "[", # yellow
        (128, 128, 0): "]", # darkyellow
        (0, 255, 255): "R", # cyan
        (0, 128, 128): "L" # darkcyan
    }


    def __init__(self):
        super(Brainloller, self).__init__()
        self.brainfuck = Brainfuck()


    def eval(self, image, stdout=None, stdin=None):
        """
        Evaluates the Brainloller program stored in image.

        See:
            pyfuck.brainfuck.Brainfuck.eval()

        Args:
            image: An image containing the Brainloller program.
            stdout: see Brainfuck.eval()
            stdin: see Brainfuck.eval()

        Raises:
            AttributeError, EOFError, ValueError

        Examples:
            >>> image = PNG().load("test/assets/hello_world_brainloller.png")
            >>> b.eval(image)
            Hello World!
        """
        if not isinstance(image, PNG):
            raise AttributeError("Image is not an instance of pyfuck.png.PNG.")

        program = []

        pcX = 0 # = program counter X
        pcY = 0 # = program counter Y
        NORTH, EAST, SOUTH, WEST = range(4)
        way = EAST # program counter way

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

        self.brainfuck.eval("".join(program), stdout, stdin)



def main():
    logging.basicConfig(level=logging.INFO)
    # TODO



if __name__ == '__main__':
    main()
