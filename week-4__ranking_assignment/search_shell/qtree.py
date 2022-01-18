#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import logging
import re

from index.normalizer import TextNormalizer

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('qtree')

# для простоты мы отказываемся от сложных конструкций со скобками или операторами
# в этот раз мы считаем, что строка запроса состоит только из термов и все они должны быть в документе


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
        regexp = re.compile(r'\s+')
        raw_tokens = regexp.split(self.expression)
        raw_tokens = [token.strip() for token in raw_tokens if token.strip() != '']

        self.tokens = []
        for token in raw_tokens:
            self.tokens.append(self._simplify_token(token))

    def get_terms(self):
        return self.tokens


class QueryTree:
    tokenizer = None

    def __init__(self, expression_string, lemmatizer):
        self.tokenizer = Tokenizer(expression_string, lemmatizer)
        self.tokenizer.tokenize()

    def extract_terms(self):
        return self.tokenizer.get_terms()

    def left_root_right_print(self):
        return '' if self.tokenizer.tokens is None else ' '.join(self.tokenizer.tokens)

    def left_right_root_execute(self, value_map):
        if self.tokenizer.tokens is None:
            return None
        else:
            # value_map = { term : { doc : [positions] } }
            doc_lists = []
            for t in self.tokenizer.tokens:
                doc_lists.append(list(value_map.get(t, {}).keys()))
            logger.info("doc_lists={}".format(str(doc_lists)))
            docs_all_terms = set(doc_lists[0])
            for i in range(1, len(doc_lists)):
                docs_all_terms = docs_all_terms.intersection(set(doc_lists[i]))
            logger.info("docs_all_terms={}".format(str(docs_all_terms)))

            result_map = dict()
            # result_map = { doc : { term : [positions] } }
            for doc in docs_all_terms:
                result_map[doc] = {}
                for t in self.tokenizer.tokens:
                    result_map[doc][t] = value_map[t][doc]

            # ВАШ КОД ЗДЕСЬ!

            # нужно написать код, который строит итоговый словарь только для тех документов,
            # в которых встречаются _все_ слова из запроса

            return result_map
