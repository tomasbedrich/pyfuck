#!/usr/bin/env python3


import unittest
import doctest
import sys

import pyfuck
from pyfuck.brainfuck import Brainfuck


class TestBrainfuck(unittest.TestCase):

    def setUp(self):
        self.bf = Brainfuck()

    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.brainfuck, extraglobs={"b": self.bf})
        self.assertEqual(result.failed, 0)

    @unittest.skipUnless(sys.stdout.isatty(), "Needs interactive shell.")
    def test_eval(self):
        print("\nInteractive test - please input characters (end test by pressing space bar):")
        self.bf.eval("+[,.--------------------------------]")
        print()


if __name__ == "__main__":
    unittest.main()
