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
        tkzr = Tokenizer("meat OR !(apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'meat'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.NOT, None),
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
        tkzr = Tokenizer("!apple", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.NOT, None), Token(TokenType.TERM, 'apple')])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'), Token(TokenType.NOT, None)])

    def test_short_not_postfix(self):
        tkzr = Tokenizer("!(apple AND grapes)", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.NOT, None),
                                       Token(TokenType.LEFT_BR, None),
                                       Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.RIGHT_BR, None)])
        tkzr.postfix()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'apple'),
                                       Token(TokenType.TERM, 'grapes'),
                                       Token(TokenType.AND, None),
                                       Token(TokenType.NOT, None)])

    def test_complex_postfix(self):
        tkzr = Tokenizer("meat OR !(apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        tkzr.tokenize()
        self.assertEqual(tkzr.tokens, [Token(TokenType.TERM, 'meat'),
                                       Token(TokenType.OR, None),
                                       Token(TokenType.NOT, None),
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
                                       Token(TokenType.NOT, None),
                                       Token(TokenType.OR, None)])

    def test_simple_tree(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_root_right_print(), str(Token(TokenType.TERM, 'apple')))

    def test_complex_tree(self):
        qt = QueryTree("meat OR !(apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        self.assertEqual(
            qt.left_root_right_print(),
            str(Token(TokenType.TERM, 'meat')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.NOT, None)) +
            str(Token(TokenType.LEFT_BR, None)) +
            str(Token(TokenType.TERM, 'apple')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'grapes')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.LEFT_BR, None)) +
            str(Token(TokenType.TERM, 'lemon')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.TERM, 'ginger')) +
            str(Token(TokenType.RIGHT_BR, None)) +
            str(Token(TokenType.RIGHT_BR, None)))

    def test_complex_tree_eq_level(self):
        qt = QueryTree("meat OR !((apple AND grapes) AND (lemon AND ginger))", self.lemmatizer)
        self.assertEqual(
            qt.left_root_right_print(),
            str(Token(TokenType.TERM, 'meat')) +
            str(Token(TokenType.OR, None)) +
            str(Token(TokenType.NOT, None)) +
            str(Token(TokenType.LEFT_BR, None)) +
            str(Token(TokenType.TERM, 'apple')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'grapes')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'lemon')) +
            str(Token(TokenType.AND, None)) +
            str(Token(TokenType.TERM, 'ginger')) +
            str(Token(TokenType.RIGHT_BR, None)))

    def test_simple_tree_execution(self):
        qt = QueryTree("apple", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute({"apple": 0b100}, 3), 0b100)

    def test_complex_tree_execution(self):
        qt = QueryTree("meat OR !(apple AND grapes AND (lemon OR ginger))", self.lemmatizer)
        self.assertEqual(qt.left_right_root_execute(
            {
                # res:    0b100111101
                "meat":   0b100001100,
                # NOT   : 0b100111001
                # AND   : 0b011000110
                "apple":  0b011100110,
                "grapes": 0b011011110,
                # l or g: 0b011110110
                "lemon":  0b011010110,
                "ginger": 0b001110110
             },
            9), 0b100111101)


if __name__ == '__main__':
    unittest.main()
