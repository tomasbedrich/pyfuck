#!/usr/bin/env python3



import unittest
import doctest
import logging
import io

import pyfuck
from pyfuck.brainfuck import Brainfuck



class TestBrainfuck(unittest.TestCase):

    def setUp(self):
        self.bf = Brainfuck()
        self.stdout = io.StringIO() # output buffer


    def test_eval(self):
        program = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."
        self.bf.eval(program, stdout=self.stdout)
        self.assertEqual(self.stdout.getvalue(), "Hello World!\n")


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.brainfuck, extraglobs={"b": self.bf})
        self.assertEqual(result.failed, 0)


    def tearDown(self):
        self.stdout.close()



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
