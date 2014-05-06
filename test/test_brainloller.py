#!/usr/bin/env python3



import unittest
import doctest
import logging
import io

import pyfuck
from pyfuck.brainloller import Brainloller
from pyfuck.png import PNG



class TestBrainloller(unittest.TestCase):


    def setUpClass():
        logging.basicConfig(level=logging.INFO)


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.brainloller)
        self.assertEqual(result.failed, 0)


    def test_to_brainloller(self):
        with open("test/assets/hello_world.bf") as f:
            image = Brainloller().to_brainloller(f.read())
        ref = PNG().load("test/assets/hello_world_brainloller_inline.png")
        self.assertEqual(ref, image)



if __name__ == "__main__":
    unittest.main()
