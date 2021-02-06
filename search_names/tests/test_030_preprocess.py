#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for secc_caste_ln.py
"""

import os
import shutil
import unittest
from search_names import preprocess
from . import capture


class TestPreprocess(unittest.TestCase):

    def setUp(self):
        self.input = 'examples/preprocess/augmented_clean_names.csv'
        self.output = 'deduped_augmented_clean_names.csv'

    def tearDown(self):
        os.unlink(self.output)

    def test_clean_names(self):
        preprocess(self.input, drop_patterns=['Barak Obama', 'Michael Jackson'])
        self.assertTrue(os.path.exists(self.output))


if __name__ == '__main__':
    unittest.main()
