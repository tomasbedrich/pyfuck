#!/usr/bin/env python3



import unittest
import doctest
import logging
import io
import sys

import pyfuck
from pyfuck.braincopter import Braincopter
from pyfuck.png import PNG



class TestBraincopter(unittest.TestCase):


    def setUp(self):
        self.bl = Braincopter()


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.braincopter, extraglobs={"b": self.bl})
        self.assertEqual(result.failed, 0)


    @unittest.skipUnless(sys.stdout.isatty(), "Needs interactive shell.")
    def test_eval(self):
        logging.info("Loading PNG...")
        image = PNG("test/assets/lost_kingdom.png")
        logging.info("PNG load done.")
        Braincopter().eval(image)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
