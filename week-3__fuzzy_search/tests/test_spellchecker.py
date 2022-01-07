#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import datetime
import logging
from unittest import TestCase
from spellchecker.spellchecker import Spellchecker
from spellchecker.dictionary import Dictionary
import tempfile

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('spellchecker')


class SpellcheckerTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(SpellcheckerTestCase, self).__init__(*args, **kwargs)

        self.dictionary = Dictionary()
        self.dictionary.build('data/test_queries.txt')

    def testLevenshteinDeistance(self):
        self.assertEqual(Spellchecker.levenshtein_distance('кошка', 'собака'), 3)
        self.assertEqual(Spellchecker.levenshtein_distance('кошка', 'кошка'), 0)
        self.assertEqual(Spellchecker.levenshtein_distance('валюда', 'валюта'), 1)

    def testIsCorrect(self):
        sc = Spellchecker(self.dictionary)
        self.assertEqual(sc.is_correct('стекло'), True)
        self.assertEqual(sc.is_correct('стикло'), False)

    def testGetCandidates(self):
        sc = Spellchecker(self.dictionary)

        a = datetime.datetime.now()
        self.assertEqual(sc.get_candidates('стикло'), ['стекло'])
        b = datetime.datetime.now()
        delta = b - a
        logger.info("testGetCandidates: {}".format(delta))

    def testGetCandidatesFast(self):
        sc = Spellchecker(self.dictionary)

        a = datetime.datetime.now()
        self.assertEqual(sc.get_candidates_fast('стикло'), ['стекло'])
        b = datetime.datetime.now()
        delta = b - a
        logger.info("testGetCandidatesFast: {}".format(delta))

    def testMeasureGetCandidatesFast(self):
        sc = Spellchecker(self.dictionary)

        a = datetime.datetime.now()
        for _ in range(10):
            self.assertEqual(sc.get_candidates_fast('стикло'), ['стекло'])
        b = datetime.datetime.now()
        delta = b - a
        logger.info("testMeasureGetCandidatesFast: {}".format(delta))
