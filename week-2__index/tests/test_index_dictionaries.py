#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from index.wrapper import Dictionary

import os.path


class IndexDictionariesTestCase(TestCase):
    dictionary_path = "./test.dict"

    def tearDown(self):
        if os.path.exists(self.dictionary_path):
            os.remove(self.dictionary_path)

    def test_dict_rw(self):
        dictionary = Dictionary()
        dictionary.add_elem("a", 1)
        dictionary.add_elem("b", 2)
        dictionary.add_elem("cd", 3)
        dictionary.add_elem("bazingaaaaaaa", 4)
        dictionary.add_elem("c", 5)

        dictionary.save_dict(self.dictionary_path)

        another_dictionary = Dictionary()
        another_dictionary.load_dict(self.dictionary_path)

        self.assertEqual(5, len(another_dictionary.d))
        self.assertTrue("a" in another_dictionary.d)
        self.assertTrue("b" in another_dictionary.d)
        self.assertTrue("c" in another_dictionary.d)
        self.assertTrue("cd" in another_dictionary.d)
        self.assertTrue("bazingaaaaaaa" in another_dictionary.d)

        reverted_dictionary = Dictionary()
        reverted_dictionary.load_dict(self.dictionary_path, True)

        self.assertEqual(5, len(reverted_dictionary.d))
        for i in range(1, 5):
            self.assertTrue(i in reverted_dictionary.d)

        self.assertEqual("a", reverted_dictionary.d[1])
        self.assertEqual("b", reverted_dictionary.d[2])
        self.assertEqual("c", reverted_dictionary.d[5])
        self.assertEqual("cd", reverted_dictionary.d[3])
        self.assertEqual("bazingaaaaaaa", reverted_dictionary.d[4])

    def test_dict_duplicates(self):
        dictionary = Dictionary(True)
        dictionary.add_elem("a", 1)
        dictionary.add_elem("b", 1)
        dictionary.add_elem("cd", 5)
        dictionary.add_elem("bazingaaaaaaa", 4)
        dictionary.add_elem("a", 5)
        dictionary.add_elem("b", 6)
        dictionary.add_elem("cd", 7)
        dictionary.add_elem("b", 1)
        dictionary.add_elem("b", 1)
        dictionary.add_elem("b", 10)
        dictionary.add_elem("bazingaaaaaaa", 11)
        dictionary.add_elem("b", 12)

        self.assertEqual(4, len(dictionary.d))
        self.assertTrue("a" in dictionary.d)
        self.assertEqual(1, dictionary.d["a"])
        self.assertTrue("b" in dictionary.d)
        self.assertEqual(2, dictionary.d["b"])
        self.assertFalse("c" in dictionary.d)
        self.assertTrue("cd" in dictionary.d)
        self.assertEqual(5, dictionary.d["cd"])
        self.assertFalse("bazinga" in dictionary.d)
        self.assertTrue("bazingaaaaaaa" in dictionary.d)
        self.assertEqual(4, dictionary.d["bazingaaaaaaa"])

    def test_dict_cyrillic(self):
        dictionary = Dictionary()
        dictionary.add_elem(u"яблоко", 1)
        dictionary.add_elem(u"груша", 42)
        dictionary.add_elem(u"груша", 43)
        dictionary.add_elem("123", 2)

        self.assertEqual(3, len(dictionary.d))
        self.assertTrue(u"яблоко" in dictionary.d)
        self.assertTrue(u"груша" in dictionary.d)
        self.assertTrue(u"123" in dictionary.d)

        dictionary.save_dict(self.dictionary_path)

        another_dictionary = Dictionary()
        another_dictionary.load_dict(self.dictionary_path)

        self.assertEqual(3, len(another_dictionary.d))
        self.assertTrue(u"яблоко" in another_dictionary.d)
        self.assertTrue(u"груша" in another_dictionary.d)
        self.assertTrue(u"123" in another_dictionary.d)


if __name__ == '__main__':
    unittest.main()