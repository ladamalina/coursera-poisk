#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from unittest import TestCase
import tempfile

from spellchecker.dictionary import Dictionary


class DictionaryTestCase(TestCase):
    def testGetWords(self):
        test_str = u"где проверить очерёдность в доу сургута"
        self.assertEqual(Dictionary.get_words(test_str),
                         [u'где', u'проверить', u'очерёдность', u'в', u'доу', u'сургута'])

    def testGetWordsNumeric(self):
        test_str = u"клипы шансона смотреть бесплатно 2015"
        self.assertEqual(Dictionary.get_words(test_str),
                         [u'клипы', u'шансона', u'смотреть', u'бесплатно'])

    def testGetWordsHyphen(self):
        test_str = u"купить компьютер пдп-1"
        self.assertEqual(Dictionary.get_words(test_str),
                         [u'купить', u'компьютер'])

    def testGetWordsHyphen2(self):
        test_str = u"по-отечески"
        self.assertEqual(Dictionary.get_words(test_str),
                         [u'по-отечески'])

    def testGetWordsUpper(self):
        test_str = u"Клипы шансона смотреть"
        self.assertEqual(Dictionary.get_words(test_str),
                         [u'клипы', u'шансона', u'смотреть'])

    def testBuild(self):
        d = Dictionary()
        d.build('data/test_queries.txt')
        self.assertEqual(d.size(), 41)
        self.assertEqual(d.get('тест'), 0)
        self.assertEqual(d.get('стекло'), 13)
        self.assertEqual(d.get('время'), 8)
        self.assertEqual(d.get('iphone'), 1)
        self.assertEqual(d.get('5'), 0)

    def testBuildThreshold(self):
        d = Dictionary()
        d.build('data/test_queries.txt', 5)
        self.assertEqual(d.size(), 3)
        self.assertEqual(d.get('тест'), 0)
        self.assertEqual(d.get('стекло'), 13)
        self.assertEqual(d.get('время'), 8)
        self.assertEqual(d.get('iphone'), 0)

    def testLoadSave(self):
        t = tempfile.NamedTemporaryFile(delete=True)
        temp_file_name = t.name

        d = Dictionary()
        d.build('data/test_queries.txt')
        d.save(temp_file_name)

        d2 = Dictionary(temp_file_name)

        self.assertDictEqual(d.words, d2.words)

    def testSoundex(self):
        self.assertEqual(Dictionary.soundex('ammonium'), 'A555')
        self.assertEqual(Dictionary.soundex('implementation'), 'I514')
        self.assertEqual(Dictionary.soundex('Robert'), 'R163')
        self.assertEqual(Dictionary.soundex('аммониум'), 'А555')
        self.assertEqual(Dictionary.soundex('стекло'), 'С324')
        self.assertEqual(Dictionary.soundex('стикло'), 'С324')