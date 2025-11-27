#!/usr/bin/env python

"""
Tests for secc_caste_ln.py
"""

import os
import unittest

from search_names import merge_supp


class TestMergeSupp(unittest.TestCase):

    def setUp(self):
        self.input = 'examples/merge_supp_data/sample_in.csv'
        self.prefixed = 'examples/merge_supp_data/prefixes.csv'
        self.nick_name = 'examples/merge_supp_data/nick_names.txt'
        self.output = 'augmented_clean_names.csv'

    def tearDown(self):
        os.unlink(self.output)

    def test_merge_supp(self):
        merge_supp(self.input, prefix_file=self.prefixed, nickname_file=self.nick_name)
        self.assertTrue(os.path.exists(self.output))


if __name__ == '__main__':
    unittest.main()
