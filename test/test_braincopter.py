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


    @unittest.skipUnless(sys.stdout.isatty(), "Needs interactive shell.")
    def test_eval(self):
        logging.info("Loading PNG...")
        image = PNG().load("test/assets/lost_kingdom.png")
        logging.info("PNG load done.")

        logging.info("Braincopter => Brainfuck conversion started.")
        program = Braincopter().to_brainfuck(image)
        logging.info("Conversion done.")
        
        Brainfuck().eval(program)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
