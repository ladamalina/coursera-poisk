#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import logging
import sys

from urllib.parse import unquote

from index.wrapper import Wrapper
from search_shell.qtree import QueryTree

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('shell')


class Shell:
    wrapper = None
    main_path = None
    tree = None

    def __init__(self, main_path):
        self.main_path = main_path

    def fill_from_index(self, terms):
        res = {}

        for term in terms:
            key = self.wrapper.words_dict.get_key(term)
            if key is not None:
                res[term] = self.wrapper.index.extract_inverted_list(key)
        return res

    def decipher_query_results(self, query_result):
        doc_list = []
        for doc_id in query_result:
            doc_tuple = (self.wrapper.docs_dict.d[doc_id], self.count_rank(query_result[doc_id]))
            doc_list.append(doc_tuple)
        doc_list.sort(key=lambda tup: -tup[1])
        return (len(doc_list), doc_list[:10])  # top-10

    def count_rank(self, doc_result_map):
        # doc_result_map = { term : [positions] }
        positions_list = []
        for term in doc_result_map:
            for position in doc_result_map[term]:
                positions_list.append((position, term))
        positions_list.sort(key=lambda tup: tup[0])
        terms_occurances = {term: 0 for term in doc_result_map}
        start = 0
        min_valid_range = 100500
        min_valid_start = 100500
        for end in range(len(positions_list)):
            end_tuple = positions_list[end]
            start_tuple = positions_list[start]
            terms_occurances[end_tuple[1]] = terms_occurances[end_tuple[1]]+1

            while terms_occurances[start_tuple[1]] > 1:
                terms_occurances[start_tuple[1]] = terms_occurances[start_tuple[1]] - 1
                start = start + 1
                start_tuple = positions_list[start]

            if len([x for x in terms_occurances.values() if x == 0]) == 0:
                full_range = end_tuple[0] - start_tuple[0] + 1
                if full_range < min_valid_range:
                    min_valid_range = full_range
                    min_valid_start = start_tuple[0] + 1

        return 1000./min_valid_start + 100./min_valid_range

    @staticmethod
    def human_readable_url(raw_url):
        return unquote(raw_url)

    def run(self):
        logger.info(msg="Start index shell")
        self.wrapper = Wrapper(self.main_path)

        while True:
            input_str = ''.join(elem for elem in input(">> "))

            if input_str == "quit":
                return

            tree = QueryTree(input_str, self.wrapper.lemmatizer)
            terms = tree.extract_terms()
            res_map = self.fill_from_index(terms)
            if res_map is None:
                print("Sorry, I cannot execute your query")
            else:
                query_result = tree.left_right_root_execute(res_map)
                if query_result is None:
                    print("Sorry, I found nothing")
                else:
                    docs_result = self.decipher_query_results(query_result)
                    print("Total: " + str(docs_result[0]) + " doc(s) found")
                    print('\n'.join("r = " + str(doc_rank) + " " + self.human_readable_url(doc_name) for (doc_name, doc_rank) in docs_result[1]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.fatal(msg="No input path were given")
    Shell(sys.argv[1]).run()
