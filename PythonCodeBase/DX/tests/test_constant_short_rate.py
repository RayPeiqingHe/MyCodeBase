__author__ = 'Ray'

import dx.constant_short_rate as cr
from datetime import timedelta

import unittest

class TestConstantShortRate(unittest.TestCase):
    def test_get_discount_factors(self):
        r = cr.constant_short_rate('short_rate', 0.05)

        date_list = []


if __name__ == '__main__':
    unittest.main()


