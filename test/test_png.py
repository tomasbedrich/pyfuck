#!/usr/bin/env python3


import unittest
import doctest

import pyfuck
from pyfuck.png import PNG


class TestPNG(unittest.TestCase):

    def test_doctests(self):
        """
        Runs doctests.
        """
        import random
        result = doctest.testmod(pyfuck.png, extraglobs={"random": random})
        self.assertEqual(result.failed, 0)

    def test_filters(self):
        """
        Tests PNG line filtering.
        """
        self.assertEqual(PNG().load("test/assets/filterSub.png").pixels[-2][-1], (8, 70, 255))
        self.assertEqual(PNG().load("test/assets/filterUp.png").pixels[-2][-1], (8, 70, 255))
        self.assertEqual(PNG().load("test/assets/filterAverage.png").pixels[-2][-1], (8, 70, 255))
        self.assertEqual(PNG().load("test/assets/filterPaeth.png").pixels[-2][-1], (8, 70, 255))

    # TODO add palette test


if __name__ == "__main__":
    unittest.main()
