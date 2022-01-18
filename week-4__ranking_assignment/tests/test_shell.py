from unittest import TestCase

from search_shell.shell import Shell


class ShellTestCase(TestCase):
    def testRankCount1Term(self):
        shell = Shell("")
        doc_result_map = {"term1": [1, 5, 8]}
        rank = shell.count_rank(doc_result_map)
        # min_interval = [1]
        # 1000/2 + 100/1 = 600
        self.assertEqual(600, rank)

    def testRankCountSeveralTerms(self):
        shell = Shell("")
        doc_result_map = {"term1": [1, 3, 10, 45, 47],
                          "term2": [7, 46, 49],
                          "term3": [4, 44, 48]}
        rank = shell.count_rank(doc_result_map)
        # min_interval = [44, 46]
        # 1000/45 + 100/3 = 55.55(5)
        self.assertTrue(abs(55.55556 - rank) < 0.0001)
