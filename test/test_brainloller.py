#!/usr/bin/env python3



import unittest
import doctest
import logging
import io

import pyfuck
from pyfuck.brainloller import Brainloller



class TestBrainloller(unittest.TestCase):


    def setUp(self):
        self.bl = Brainloller()


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.brainloller, extraglobs={"b": self.bl})
        self.assertEqual(result.failed, 0)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
