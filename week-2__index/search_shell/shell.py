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
            res[term] = [] if key is None else self.wrapper.index.extract_inverted_list(key)
        return res

    def decipher_query_results(self, query_result):
        doc_list = []
        for doc_id in query_result:
            doc_list.append(self.wrapper.docs_dict.d[doc_id])
        return doc_list

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
            query_result = tree.left_right_root_execute(res_map)
            if res_map is None:
                print("Sorry, I cannot execute your query")
            else:
                docs_result = self.decipher_query_results(query_result)
                print(str(len(docs_result)) + " doc(s) found")
                print('\n'.join(self.human_readable_url(doc_name) for doc_name in docs_result))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.fatal(msg="No input path were given")
    Shell(sys.argv[1]).run()
