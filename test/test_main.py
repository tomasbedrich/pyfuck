#!/usr/bin/env python3



import unittest
import logging
import argparse
import io
import sys
import itertools
from tempfile import NamedTemporaryFile as mktemp
from os import unlink

import pyfuck
import pyfuck.__main__ as main



class TestInterpreter(unittest.TestCase):


    hello_worlds = list(map(lambda f: "test/assets/hello_world." + f, ["brainfuck", "brainloller.png", "braincopter.png"]))


    def setUp(self):
        # replace stdout and save orig
        self.orig = sys.stdout


    def tearDown(self):
        # revert changes
        sys.stdout = self.orig
        

    def test_run(self):
        # try to run each hello world
        for filename in self.hello_worlds:
            with self.subTest(filename):
                sys.stdout = io.StringIO()
                args = main.parser_main.parse_args(["run", filename])
                main.Interpreter(args).run()
                self.assertEqual("Hello World!\n", sys.stdout.getvalue())
            

    def test_conversion(self):
        for source, output in itertools.product(self.hello_worlds, ["brainfuck", "brainloller", "braincopter"]):
            with self.subTest(source=source, output=output):
                # temp conversion destination
                tmp = mktemp(delete=False)
                tmp.close()
                
                # convert
                args = main.parser_main.parse_args(["convert", "-o", output, source, tmp.name, "-i", "test/assets/earth.png"])
                # print(args)
                main.Interpreter(args).convert()

                # run
                args = main.parser_main.parse_args(["run", tmp.name])
                sys.stdout = io.StringIO()
                main.Interpreter(args).run()
                
                self.assertEqual("Hello World!\n", sys.stdout.getvalue())

                # cleanup
                unlink(tmp.name)


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    unittest.main()
