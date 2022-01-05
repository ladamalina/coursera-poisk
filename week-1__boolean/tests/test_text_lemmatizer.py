import unittest
from unittest import TestCase

from index.lemmatizer import TextLemmatizer


class TextLemmatizerTestCase(TestCase):
    def test_basics(self):
        lemmatizer = TextLemmatizer()
        self.assertEqual("яблоко", lemmatizer.lemmatize("яблоками"))
        self.assertEqual("удивительный", lemmatizer.lemmatize("удивительнейшая"))


if __name__ == '__main__':
    unittest.main()
