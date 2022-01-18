import unittest
from unittest import TestCase

from search_shell.qtree import Tokenizer
from search_shell.qtree import QueryTree

from index.lemmatizer import TextLemmatizer


class QTreeTestCase(TestCase):
    lemmatizer = None

    def setUp(self):
        self.lemmatizer = TextLemmatizer()

    def test_simple_tokenizer(self):
        tkzr = Tokenizer("apple grapes", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, ['apple', 'grapes'])

    def test_complex_tokenizer(self):
        tkzr = Tokenizer("apple  grapes lemon", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, ['apple', 'grapes', 'lemon'])

    def test_simple_tree(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_root_right_print(), str('apple'))

    def test_complex_tree(self):
        qt = QueryTree("apple  grapes  lemon", self.lemmatizer)
        self.assertEqual(
            qt.left_root_right_print(),
            str('apple grapes lemon'))

    def test_simple_tree_execution(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute({"apple": {1: [1, 2, 3]}}), {1: {"apple": [1, 2, 3]}})

    def test_simple_tree_execution2(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute({}), {})

    def test_simple_tree_execution3(self):
        qt = QueryTree("apple lemon", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {3: [7, 8, 9]},
        }
        expected_output = {}
        self.assertEqual(qt.left_right_root_execute(input), expected_output)

    def test_simple_tree_execution4(self):
        qt = QueryTree("apple lemon grapes", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {3: [7, 8, 9]},
        }
        expected_output = {}
        self.assertEqual(qt.left_right_root_execute(input), expected_output)

    def test_simple_tree_execution5(self):
        qt = QueryTree("apple lemon", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {2: [7, 8, 9]},
        }
        expected_output = {
            2: {"apple": [4, 5, 6], "lemon": [7, 8, 9]},
        }
        self.assertEqual(qt.left_right_root_execute(input), expected_output)

    def test_simple_tree_execution6(self):
        qt = QueryTree("apple lemon", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {1: [1, 2, 3], 2: [7, 8, 9]},
        }
        expected_output = {
            1: {"apple": [1, 2, 3], "lemon": [1, 2, 3]},
            2: {"apple": [4, 5, 6], "lemon": [7, 8, 9]},
        }
        self.assertEqual(qt.left_right_root_execute(input), expected_output)

    def test_simple_tree_execution7(self):
        qt = QueryTree("apple lemon grapes", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {1: [1, 2, 3], 2: [7, 8, 9]},
        }
        expected_output = {}
        self.assertEqual(qt.left_right_root_execute(input), expected_output)

    def test_simple_tree_execution7(self):
        qt = QueryTree("apple lemon", self.lemmatizer)
        input = {
            "apple": {1: [1, 2, 3], 2: [4, 5, 6]},
            "lemon": {1: [1, 2, 3], 2: [7, 8, 9]},
        }
        expected_output = {
            1: {"apple": [1, 2, 3], "lemon": [1, 2, 3]},
            2: {"apple": [4, 5, 6], "lemon": [7, 8, 9]},
        }
        self.assertEqual(qt.left_right_root_execute(input), expected_output)


if __name__ == '__main__':
    unittest.main()
