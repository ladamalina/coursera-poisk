#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import re
from enum import Enum

from index.normalizer import TextNormalizer


class TokenType(Enum):
    TERM = 1
    LEFT_BR = 2
    RIGHT_BR = 3
    NOT = 6
    AND = 5
    OR = 4


class Token:
    tokenType = None
    value = None

    def __init__(self, token_type, value=None):
        self.tokenType = token_type
        self.value = value

    def __eq__(self, other):
        if self.tokenType != other.tokenType:
            return False
        return (self.value is None and other.value is None) or (self.value == other.value)

    def __lt__(self, other):
        return self.tokenType.value < other.tokenType.value

    def __le__(self, other):
        return self.tokenType.value < other.tokenType.value or self.tokenType.value == other.tokenType.value

    def __gt__(self, other):
        return self.tokenType.value > other.tokenType.value

    def __ge__(self, other):
        return self.tokenType.value > other.tokenType.value or self.tokenType.value == other.tokenType.value

    def __repr__(self):
        return '(' + self.tokenType.name + ', ' + ('None' if self.value is None else self.value) + ')'

    def __str__(self):
        return '(' + self.tokenType.name + ', ' + ('None' if self.value is None else self.value) + ')'

    def is_term(self):
        return self.tokenType == TokenType.TERM

    def is_brace(self):
        return self.tokenType == TokenType.LEFT_BR or self.tokenType == TokenType.RIGHT_BR

    def is_lbrace(self):
        return self.tokenType == TokenType.LEFT_BR

    def is_rbrace(self):
        return self.tokenType == TokenType.RIGHT_BR

    def is_not(self):
        return self.tokenType == TokenType.NOT


class TreeNode:
    token = None
    left = None
    right = None

    def __init__(self, token):
        self.token = token

    @staticmethod
    def form_level_for_print(main_token, lower_node):
        if lower_node is None:
            return ''
        if main_token > lower_node.token and not lower_node.token.is_term():
            return str(Token(TokenType.LEFT_BR)) + \
                lower_node.left_root_right_print() + \
                str(Token(TokenType.RIGHT_BR))
        return lower_node.left_root_right_print()

    def left_root_right_print(self):
        if self.token.is_not():
            return str(self.token) + \
                str(Token(TokenType.LEFT_BR)) + \
                self.left.left_root_right_print() + \
                str(Token(TokenType.RIGHT_BR))

        return self.form_level_for_print(self.token, self.left) + \
            str(self.token) + \
            self.form_level_for_print(self.token, self.right)

    @staticmethod
    def execute_bit_not(n, numbits=8):
        res_not = ((1 << numbits) - 1 - n)
        return res_not

    def left_right_root_execute(self, values_map, docs_count):
        left_value = 0 if self.left is None else self.left.left_right_root_execute(values_map, docs_count)
        right_value = 0 if self.right is None else self.right.left_right_root_execute(values_map, docs_count)

        if self.token.is_term():
            return values_map[self.token.value]
        elif self.token.is_not():
            return self.execute_bit_not(left_value, docs_count)
        elif self.token.tokenType == TokenType.OR:
            return left_value | right_value
        elif self.token.tokenType == TokenType.AND:
            return left_value & right_value


class Tokenizer:
    expression = None
    tokens = None
    iterator = 0
    lemmatizer = None

    def __init__(self, exp, lemmatizer):
        self.expression = exp
        self.lemmatizer = lemmatizer

    def _simplify_token(self, token):
        lemma = self.lemmatizer.lemmatize(token)
        return TextNormalizer.lower_case(lemma)

    def tokenize(self):
        regexp = re.compile(r'(\bAND\b|\bOR\b|!|\(|\))')
        raw_tokens = regexp.split(self.expression)
        raw_tokens = [token.strip() for token in raw_tokens if token.strip() != '']

        self.tokens = []
        for token in raw_tokens:
            if token == 'AND':
                self.tokens.append(Token(TokenType.AND))
            elif token == 'OR':
                self.tokens.append(Token(TokenType.OR))
            elif token == '!':
                self.tokens.append(Token(TokenType.NOT))
            elif token == '(':
                self.tokens.append(Token(TokenType.LEFT_BR))
            elif token == ')':
                self.tokens.append(Token(TokenType.RIGHT_BR))
            else:
                self.tokens.append(Token(TokenType.TERM, self._simplify_token(token)))

    def postfix(self):
        operator_stack = []
        result = []

        for token in self.tokens:
            if token.is_term():
                result.append(token)
            elif token.is_lbrace():
                operator_stack.append(token)
            elif token.is_rbrace():
                op = operator_stack.pop()
                while not op.is_lbrace():
                    result.append(op)
                    op = operator_stack.pop()
            else:
                while len(operator_stack) > 0:
                    op = operator_stack.pop()
                    if op >= token:
                        result.append(op)
                    else:
                        operator_stack.append(op)
                        break
                operator_stack.append(token)

        while len(operator_stack) > 0:
            op = operator_stack.pop()
            result.append(op)

        self.tokens = result

    def get_terms(self):
        res = []
        for token in self.tokens:
            if token.is_term() and token.value not in res:
                res.append(token.value)
        return res


class QueryTree:
    tokenizer = None
    root = None

    def __init__(self, expression_string, lemmatizer):
        self.tokenizer = Tokenizer(expression_string, lemmatizer)
        self.tokenizer.tokenize()
        self.tokenizer.postfix()
        self.parse()

    def parse(self):
        stack = []
        for token in self.tokenizer.tokens:
            node = TreeNode(token)
            if token.is_term():
                stack.append(node)
            else:
                if token.tokenType == TokenType.NOT:
                    node.left = stack.pop()
                    node.right = None
                else:
                    node.right = stack.pop()
                    node.left = stack.pop()
                stack.append(node)
        self.root = stack.pop()

    def extract_terms(self):
        return self.tokenizer.get_terms()

    def print_tree(self):
        self.root.print_tree()

    def left_root_right_print(self):
        return '' if self.root is None else self.root.left_root_right_print()

    def left_right_root_execute(self, value_map, docs_count):
        return self.root.left_right_root_execute(value_map, docs_count)
