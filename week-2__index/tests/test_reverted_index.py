#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from index.wrapper import RevertIndex


class IndexRITestCase(TestCase):

    def test_index_basic(self):
        doc_ids = [1, 2, 3, 4, 5, 6]
        word_ids = [15, 27, 39, 43, 53, 55]
        index = RevertIndex()

        for word_id in word_ids:
            for doc_id in doc_ids:
                # индекс - по умолчанию для любой пары слово-документ возвращается False
                self.assertFalse(index.value(word_id, doc_id))

        documents = {
            15: [2, 5],
            27: [1],
            39: [1, 3, 4],
            43: [6],
            53: [4, 5],
            55: []
        }

        for word, docs in documents.items():
            for doc in docs:
                index.add_pair(word, doc)

        for word_id in word_ids:
            for doc_id in doc_ids:
                if doc_id in documents[word_id]:
                    self.assertTrue(index.value(word_id, doc_id))
                else:
                    self.assertFalse(index.value(word_id, doc_id))

    def test_index_extract_inverted_lists(self):
        index = RevertIndex()

        documents = {
            15: [2, 5],
            27: [1],
            39: [1, 3, 4],
            43: [6],
            53: [4, 5]
        }

        for word, docs in documents.items():
            for doc in docs:
                index.add_pair(word, doc)

        for word, docs in documents.items():
            self.assertEqual(docs, index.extract_inverted_list(word))


if __name__ == '__main__':
    unittest.main()