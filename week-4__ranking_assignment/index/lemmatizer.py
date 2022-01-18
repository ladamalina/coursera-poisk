#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import logging
import pymorphy2

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('lemmatizer')


class TextLemmatizer:
    def __init__(self):
        self.cache = dict()
        self.morph = pymorphy2.MorphAnalyzer()

    def lemmatize(self, word):
        if word in self.cache:
            return self.cache[word]

        candidates = self.morph.parse(word)
        if len(candidates) == 0:
            result = word
        else:
            result = candidates[0].normal_form

        self.cache[word] = result

        return result
