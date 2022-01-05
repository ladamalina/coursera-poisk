#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from index.wrapper import Matrix
from index.wrapper import Dictionary

import os.path


class IndexMatrixTestCase(TestCase):

    def test_matrix_basic(self):
        doc_ids = [1, 2, 3, 4, 5, 6]
        word_ids = [15, 27, 39, 43, 53, 55]
        matrix = Matrix()

        for word_id in word_ids:
            for doc_id in doc_ids:
                # матрица не заполнена - по умолчанию для любой пары слово-документ возвращается False
                self.assertFalse(matrix.value(word_id, doc_id))

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
                matrix.activate(word, doc)

        for word_id in word_ids:
            for doc_id in doc_ids:
                if doc_id in documents[word_id]:
                    self.assertTrue(matrix.value(word_id, doc_id))
                else:
                    self.assertFalse(matrix.value(word_id, doc_id))

    def test_matrix_extract_line(self):
        matrix = Matrix()

        documents = {
            15: [2, 5],
            27: [1],
            39: [1, 3, 4],
            43: [6],
            53: [4, 5]
        }

        for word, docs in documents.items():
            for doc in docs:
                matrix.activate(word, doc)

        self.assertEqual(0b010010, matrix.extract_line(15))
        self.assertEqual(0b100000, matrix.extract_line(27))
        self.assertEqual(0b101100, matrix.extract_line(39))
        self.assertEqual(0b000001, matrix.extract_line(43))
        self.assertEqual(0b000110, matrix.extract_line(53))
        self.assertEqual(0, matrix.extract_line(54))


    def test_matrix_save_load(self):
        matrix = Matrix()
        doc_ids = [1, 2, 3, 4, 5, 6]
        word_ids = [15, 27, 39, 43, 53, 55]

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
                matrix.activate(word, doc)

        path = "/tmp/test_matrix_save_load.json"
        matrix.save_matrix(path)

        matrix2 = Matrix()
        matrix2.load_matrix(path)

        for word_id in word_ids:
            for doc_id in doc_ids:
                if doc_id in documents[word_id]:
                    self.assertTrue(matrix2.value(word_id, doc_id))
                else:
                    self.assertFalse(matrix2.value(word_id, doc_id))


if __name__ == '__main__':
    unittest.main()
