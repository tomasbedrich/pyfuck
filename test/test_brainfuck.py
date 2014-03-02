#!/usr/bin/env python3


import unittest
import logging
from pyfuck.brainfuck import Brainfuck


class TestBrainfuck(unittest.TestCase):

    def setUp(self):
        self.bf = Brainfuck()

    def test_eval(self):
        program = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        res = self.bf.eval(program)
        self.assertEqual(res, "Hello World!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()