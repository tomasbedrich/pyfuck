#!/usr/bin/env python3


import unittest
import doctest

import pyfuck
from pyfuck.braincopter import Braincopter
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


if __name__ == "__main__":
    unittest.main()
