#!/usr/bin/env python3



import unittest
import doctest
import logging

import pyfuck
from pyfuck.png import PNG



class TestPNG(unittest.TestCase):


    def test_doctests(self):
        """
        Runs doctests.
        """
        result = doctest.testmod(pyfuck.png)
        self.assertEqual(result.failed, 0)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
