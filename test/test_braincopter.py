#!/usr/bin/env python3



import unittest
import doctest
import logging
import io
import sys

import pyfuck
from pyfuck.braincopter import Braincopter
from pyfuck.brainfuck import Brainfuck
from pyfuck.png import PNG



class TestBraincopter(unittest.TestCase):


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.braincopter)
        self.assertEqual(result.failed, 0)


    def test_to_braincopter(self):
        bc = Braincopter()
        with open("test/assets/hello_world.brainfuck") as f:
            contents = f.read()
        target = PNG().load("test/assets/palette.png")
        res = bc.to_braincopter(contents, target)
        self.assertEqual(contents, bc.to_brainfuck(res))


    @unittest.skipUnless(sys.stdout.isatty(), "Needs interactive shell.")
    def test_eval(self):
        print("\nInteractive test:")
        logging.info("Loading PNG...")
        image = PNG().load("test/assets/lost_kingdom.png")
        logging.info("PNG load done.")

        logging.info("Converting Braincopter to Brainfuck.")
        program = Braincopter().to_brainfuck(image)
        logging.info("Conversion done.")
        
        Brainfuck().eval(program)
        print()



if __name__ == "__main__":
    unittest.main()
