#!/usr/bin/env python

"""
Tests for secc_caste_ln.py
"""

import os
import unittest

from search_names import clean_names


class TestCleanNames(unittest.TestCase):

    def setUp(self):
        self.input = 'examples/clean_names/sample_input.csv'
        self.output = 'clean_names.csv'

    def tearDown(self):
        os.unlink(self.output)

    def test_clean_names(self):
        clean_names(self.input)
        self.assertTrue(os.path.exists(self.output))


if __name__ == '__main__':
    unittest.main()
