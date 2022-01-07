#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import json
import logging
import sys
from index.wrapper import Dictionary
from index.wrapper import IndexPathWrapper
from index.wrapper import RevertIndex
from index.normalizer import TextNormalizer
from index.lemmatizer import TextLemmatizer

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('index_builder')


class IndexBuilder:
    ipw = None
    docs_dict = None
    words_dict = None
    index = None

    def __init__(self, path):
        self.ipw = IndexPathWrapper(path)
        self.docs_dict = Dictionary(True)
        self.words_dict = Dictionary(True)
        self.index = RevertIndex()
        self.lemmatizer = TextLemmatizer()

    def build_index(self):
        logger.info(msg="Build index")
        # read files
        with open(self.ipw.get_raw_docs_path(), "r") as in_file:
            doc_id = 0
            word_id = 1

            for line in in_file:
                doc_id = doc_id + 1
                jo = json.loads(line, 'utf-8')

                # normalize text
                text = jo["content"]
                text = TextNormalizer.join_numbers(text)
                text = TextNormalizer.clean_out_punct(text)
                text = TextNormalizer.lower_case(text)
                words = TextNormalizer.split(text)

                # lemmatize
                lemmas = [self.lemmatizer.lemmatize(word) for word in words]
                lemmas_unique = set(lemmas)

                # build dictionaries
                self.docs_dict.add_elem(str(jo["url"]), doc_id)

                for lemma in lemmas_unique:
                    new_id = self.words_dict.add_elem(lemma, word_id)
                    if new_id < word_id:
                        pass
                    else:
                        word_id = word_id+1

                    # build matrix
                    self.index.add_pair(new_id, doc_id)

        logger.info(str(self.docs_dict.dictionary_size) + " doc(s), " + str(self.words_dict.dictionary_size) + " word(s)")

        self.words_dict.save_dict(self.ipw.get_words_dict_path())
        self.docs_dict.save_dict(self.ipw.get_docs_dict_path())
        self.index.save_index(self.ipw.get_index_path())


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        logger.fatal(msg="Incorrect input")
        exit(1)
    IndexBuilder(sys.argv[1]).build_index()
