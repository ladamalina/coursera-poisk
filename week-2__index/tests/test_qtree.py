import unittest
from unittest import TestCase

from search_shell.qtree import Token
from search_shell.qtree import Tokenizer
from search_shell.qtree import TokenType
from search_shell.qtree import QueryTree

from index.lemmatizer import TextLemmatizer


class QTreeTestCase(TestCase):
    lemmatizer = None

    def setUp(self):
        self.lemmatizer = TextLemmatizer()

    def test_simple_tokenizer(self):
        tkzr = Tokenizer("apple AND grapes", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes')])

    def test_complex_tokenizer(self):
        tkzr = Tokenizer("meat OR (apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'meat'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'lemon'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.TERM, 'ginger'),
                                       Token(TokenType.RIGHT_BR, None),
                                       Token(TokenType.RIGHT_BR, None)])

    def test_simple_postfix(self):
        tkzr = Tokenizer("apple", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple')])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple')])

    def test_short_postfix(self):
        tkzr = Tokenizer("apple AND grapes", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes')])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None)])

    def test_simple_not_postfix(self):
        tkzr = Tokenizer("apple", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple')])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple')])

    def test_short_not_postfix(self):
        tkzr = Tokenizer("(apple AND grapes)", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.RIGHT_BR, None)])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None)])

    def test_complex_postfix(self):
        tkzr = Tokenizer("meat OR (apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'meat'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'lemon'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.TERM, 'ginger'),
                                       Token(TokenType.RIGHT_BR, None),
                                       Token(TokenType.RIGHT_BR, None)])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'meat'),
                                       Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'lemon'),
                                       Token(TokenType.TERM, 'ginger'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.OR, None)])

    def test_simple_tree(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_root_right_print(), str(Token(TokenType.TERM, 'apple')))

    def test_complex_tree(self):
        qt = QueryTree("meat OR (apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        self.assertEqual(
            qt.left_root_right_print(),
            str(Token(TokenType.TERM, 'meat')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.TERM, 'apple')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'grapes')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.LEFT_BR, None)) +
            str(Token(TokenType.TERM, 'lemon')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.TERM, 'ginger')) +
            str(Token(TokenType.RIGHT_BR, None)))

    def test_complex_tree_eq_level(self):
        qt = QueryTree("meat OR ((apple AND grapes) AND (lemon AND ginger))", self.lemmatizer)
        self.assertEqual(
            qt.left_root_right_print(),
            str(Token(TokenType.TERM, 'meat')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.TERM, 'apple')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'grapes')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'lemon')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'ginger')))

    def test_simple_tree_execution(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute({"apple": [1]}), [1])

    def test_complex_tree_execution(self):
        qt = QueryTree("meat OR (apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute(
            {
                # OR    : [1, 2, 3, 6, 7, 8]
                "meat":   [1, 6, 7],
                # AND   : [2, 3, 7, 8]
                "apple":  [2, 3, 4, 7, 8],
                "grapes": [2, 3, 5, 6, 7, 8],
                # l or g: [2, 3, 4, 5, 7, 8]
                "lemon":  [2, 3, 5, 7, 8],
                "ginger": [3, 4, 5, 7, 8]
             }), [1, 2, 3, 6, 7, 8])

    def test_qtree_1(self):
        qt = QueryTree("", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute(
            {
                "meat": [1, 6, 7],
                "apple": [2, 3, 4, 7, 8],
                "grapes": [2, 3, 5, 6, 7, 8],
                "lemon": [2, 3, 5, 7, 8],
                "ginger": [3, 4, 5, 7, 8]
            }), [])

    def test_qtree_2(self):
        qt = QueryTree("banana", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute(
            {
                "meat": [1, 6, 7],
                "apple": [2, 3, 4, 7, 8],
                "grapes": [2, 3, 5, 6, 7, 8],
                "lemon": [2, 3, 5, 7, 8],
                "ginger": [3, 4, 5, 7, 8]
            }), [])

    def test_qtree_3(self):
        qt = QueryTree("meat", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute(
            {
                "meat": [1, 6, 7],
                "apple": [2, 3, 4, 7, 8],
                "grapes": [2, 3, 5, 6, 7, 8],
                "lemon": [2, 3, 5, 7, 8],
                "ginger": [3, 4, 5, 7, 8]
            }), [1, 6, 7])


if __name__ == '__main__':
    unittest.main()
