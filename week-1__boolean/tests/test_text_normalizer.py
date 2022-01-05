import unittest
from unittest import TestCase

from index.normalizer import TextNormalizer


class TextNormalizerTestCase(TestCase):
    def test_join_numbers(self):
        nrmlz = TextNormalizer()
        self.assertEqual("a b c d 1 b 3", nrmlz.join_numbers("a b c d 1 b 3"))
        self.assertEqual("a b 22 c d 13 e", nrmlz.join_numbers("a b 2 2 c d 1  3 e"))
        self.assertEqual("a b c d 1-3 e", nrmlz.join_numbers("a b c d 1-3 e"))


if __name__ == '__main__':
    unittest.main()
