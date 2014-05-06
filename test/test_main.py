#!/usr/bin/env python3



import unittest
import logging
import argparse
import io
import sys

import pyfuck
import pyfuck.__main__ as main



class TestInterpreter(unittest.TestCase):


    def setUpClass():
        logging.basicConfig(level=logging.INFO)
        pass


    def test_conversion(self):
        # replace stdout and save orig
        orig = sys.stdout
        sys.stdout = io.StringIO()

        args = main.parser_main.parse_args(["run", "test/assets/hello_world.brainfuck"])
        i = main.Interpreter(args)
        i.run()

        # revert changes
        buffer = sys.stdout.getvalue()
        sys.stdout = orig
        print(buffer)



if __name__ == "__main__":
    unittest.main()
