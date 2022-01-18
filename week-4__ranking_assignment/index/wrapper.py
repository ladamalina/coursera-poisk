#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import logging
from struct import Struct
from index.lemmatizer import TextLemmatizer

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('index_wrapper')


class IndexPathWrapper:
    main_path = None

    def __init__(self, main_path):
        self.main_path = main_path

    def get_words_dict_path(self):
        return self.main_path + "/words.dic"

    def get_docs_dict_path(self):
        return self.main_path + "/docs.dic"

    def get_index_path(self):
        return self.main_path + "/idx.idx"

    def get_raw_docs_path(self):
        return self.main_path + "/raw_docs.json"


class RevertIndex:
    # в этом случае в обратном индексе хранится не только документ, в котором встречается конкретный терм
    # но и список позиций, на которых он находился в тексте
    m = None
    number_struct = Struct("<I")

    def __init__(self):
        self.m = {}

    def add_doc(self, term, doc, positions):
        if term in self.m:
            if doc in self.m[term]:
                self.m[term][doc].append(positions)
            else:
                self.m[term][doc] = positions
        else:
            # мы не проверяем наличие документа и то, на какую позицию нужно добавить его в список, в силу построения:
            # * doc_id всегда равномерно увеличиваются
            # * список позиций уже сгруппирован для конкретного терма => повторений не будет
            self.m[term] = {}
            self.m[term][doc] = positions

    def value(self, term, doc):
        if term in self.m:
            if doc in self.m[term]:
                return True

        return False

    def extract_inverted_list(self, term_id):
        return self.m[term_id] if term_id in self.m else {}

    def load_index(self, path):
        loaded_cnt = 0
        with open(path, "rb") as bin_file:
            terms_cnt = self.number_struct.unpack(bin_file.read(self.number_struct.size))[0]

            for t in range(terms_cnt):
                term_id = self.number_struct.unpack(bin_file.read(self.number_struct.size))[0]
                docs_cnt = self.number_struct.unpack(bin_file.read(self.number_struct.size))[0]

                for d in range(docs_cnt):
                    doc_id = self.number_struct.unpack(bin_file.read(self.number_struct.size))[0]
                    positions_cnt = self.number_struct.unpack(bin_file.read(self.number_struct.size))[0]
                    positions = []
                    for p in range(positions_cnt):
                        positions.append(self.number_struct.unpack(bin_file.read(self.number_struct.size))[0])
                    self.add_doc(term_id, doc_id, positions)
                    loaded_cnt = loaded_cnt + 1

        logger.info(msg="Load index from '{}'. {} element(s) loaded.".format(path, loaded_cnt))

    def save_index(self, path):
        saved_cnt = 0
        with open(path, "wb") as bin_file:
            bin_file.write(self.number_struct.pack(len(self.m)))

            for term in self.m:
                bin_file.write(self.number_struct.pack(term))
                bin_file.write(self.number_struct.pack(len(self.m[term])))

                for doc in self.m[term]:
                    bin_file.write(self.number_struct.pack(doc))
                    bin_file.write(self.number_struct.pack(len(self.m[term][doc])))
                    for position in self.m[term][doc]:
                        bin_file.write(self.number_struct.pack(position))

                    saved_cnt = saved_cnt + 1

        logger.info(msg="Save index to '{}'. {} element(s) saved.".format(path, saved_cnt))


class Dictionary:
    d = None
    rev_d = None
    build_rev = False
    dictionary_size = 0
    was_reverted = False
    number_struct = Struct("<I")

    def __init__(self, build_rev=False):
        self.build_rev = build_rev
        self.clean_start()

    def clean_start(self):
        self.d = {}
        if self.build_rev:
            self.rev_d = []
        self.dictionary_size = 0

    def load_dict(self, path, need_revert=False):
        self.clean_start()
        self.was_reverted = need_revert
        with open(path, "rb") as bin_file:
            bin_data = bin_file.read(self.number_struct.size)
            size = self.number_struct.unpack(bin_data)[0]

            for i in range(size):
                bin_data = bin_file.read(self.number_struct.size)
                string_size = self.number_struct.unpack(bin_data)[0]

                record_struct = Struct("%ds" % string_size)
                bin_data = bin_file.read(record_struct.size)
                record = (record_struct.unpack(bin_data)[0]).decode('UTF-8')

                bin_data = bin_file.read(self.number_struct.size)
                key = self.number_struct.unpack(bin_data)[0]
                if need_revert:
                    self.add_elem(key, record)
                else:
                    self.add_elem(record, key)
        logger.info(msg="Load dictionary from '" + path + "'. " + str(self.dictionary_size) + " element(s) loaded.")

    def save_dict(self, path):
        with open(path, "wb") as bin_file:
            bin_file.write(self.number_struct.pack(self.dictionary_size))

            for k in self.d.keys():
                key = k.encode('utf-8')
                key_len = len(key)
                bin_file.write(self.number_struct.pack(key_len))
                record_struct = Struct("%ds" % key_len)
                bin_file.write(record_struct.pack(key))
                bin_file.write(self.number_struct.pack(self.d[k]))
        logger.info(msg="Save dictionary to '" + path + "'. " + str(self.dictionary_size) + " element(s) saved.")

    def add_elem(self, elem, key):
        if elem in self.d:
            return self.d[elem]

        self.dictionary_size = self.dictionary_size + 1

        if self.build_rev:
            while key in self.rev_d:
                key = key + 1

            self.d[elem] = key
            for i in range(len(self.rev_d)):
                if self.rev_d[i] > key:
                    self.rev_d.insert(i, key)
                    return key
            self.rev_d.append(key)
            return key
        else:
            self.d[elem] = key
            return key

    def make_reverted(self):
        self.clean_revert()
        new_dictionary = {}
        for obj, obj_id in self.d.items():
            new_dictionary[obj_id] = obj
        self.d = new_dictionary
        self.was_reverted = True

    def clean_revert(self):
        self.build_rev = False
        self.rev_d = None

    def get_key(self, elem):
        if elem in self.d:
            return self.d[elem]
        else:
            return None


class Wrapper:
    words_dict = None
    docs_dict = None
    index = None
    lemmatizer = None

    def __init__(self, index_path):
        ipw = IndexPathWrapper(index_path)

        self.words_dict = Dictionary()
        self.words_dict.load_dict(ipw.get_words_dict_path())

        self.docs_dict = Dictionary(True)
        self.docs_dict.load_dict(ipw.get_docs_dict_path(), True)

        self.index = RevertIndex()
        self.index.load_index(ipw.get_index_path())

        self.lemmatizer = TextLemmatizer()
