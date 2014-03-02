#!/usr/bin/env python3

import unittest
from pyfuck.brainfuck import Brainfuck

class TestBrainfuck(unittest.TestCase):

    def setUp(self):
        self.bf = Brainfuck()

    def test_eval(self):
        program = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        res = self.bf.eval(program)
        self.assertEquals(res, "Hello World!")


if __name__ == "__main__":
    unittest.main()