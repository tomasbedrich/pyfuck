#!/usr/bin/env python3


import unittest
import doctest

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


if __name__ == "__main__":
    unittest.main()
