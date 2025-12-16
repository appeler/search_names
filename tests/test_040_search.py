#!/usr/bin/env python

"""
Tests for secc_caste_ln.py
"""

import os
import unittest

from search_names import search_names
from search_names.pipeline.step4_search import load_names_file


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.input = "examples/search/text_corpus.csv"
        self.name_file = "examples/preprocess/deduped_augmented_clean_names.csv"
        self.output = "search_results.csv"

    def tearDown(self):
        os.unlink(self.output)

    def test_clean_names(self):
        names = load_names_file(self.name_file)
        search_names(self.input, names=names)
        self.assertTrue(os.path.exists(self.output))


if __name__ == "__main__":
    unittest.main()
