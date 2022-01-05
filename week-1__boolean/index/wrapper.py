#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import json
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


class Matrix:
    # Эти структуры могут понадобиться вам для корректного сохранения матрицы в файл и последующего чтения
    number_struct = Struct("<I")
    number_pair_struct = Struct("<II")

    def __init__(self):
        # инициализируйте начальные значения внутренних переменных
        self._tf_idf = {}
        self._docs = []
        self._docs_set = set()

        # или не делайте ничего:
        # pass

    def activate(self, word_id, doc_id):
        # вносим в матрицу инцидентности информацию о том, что слово с id=word_id встречалось в документе с id=doc_id
        # прежде, чем приступать к реализации матрицы, следует вспомнить о том, что матрица инцидентности сильно разряжена
        # это значит, что бОльшую ее часть будут занимать 0 (в случае, если мы будем хранить в ней 1 и 0)
        # в случае с практической реализацией иногда оправдано следующее представление: вместо полноценной матрицы хранится список ненулевых элементов (их координаты)
        w_id = str(word_id)
        d_id = str(doc_id)
        if w_id not in self._tf_idf:
            self._tf_idf[w_id] = {str(d_id): True}
        self._tf_idf[w_id][d_id] = True

        if d_id not in self._docs_set:
            self._docs_set.add(d_id)
            self._docs.append(d_id)
            self._docs = sorted(self._docs)

    def value(self, word_id, doc_id):
        # возвращает True, если word_id есть в документе doc_id
        # иначе - False
        w_id = str(word_id)
        d_id = str(doc_id)

        if w_id not in self._tf_idf:
            return False
        if d_id not in self._docs_set:
            return False
        return d_id in self._tf_idf[w_id]

    def extract_line(self, word_id):
        # возвращает строку из матрицы в виде числа, двоичное представление которого отражает положение 1 и 0 в этой строке таблицы
        # Пример: 0b0110 для слова, которое есть в 2 и 3 документах (при условии, что матрица содержит информацию только о 4 документах)
        w_id = str(word_id)

        if w_id not in self._tf_idf:
            return 0

        bin_str = "".join(["1" if d_id in self._tf_idf[w_id] else "0" for d_id in self._docs])
        bin_int = int(bin_str, base=2)

        return bin_int

    def load_matrix(self, path):
        loaded_elements = 0
        with open(path, "r", encoding='utf8') as f:
            # загружаем матрицу из файла
            # лучше всего использовать для записи и чтения данных struct.pack/unpack
            # пример можно найти в Dictionary.load_dict
            self._tf_idf = json.load(f)
            self._docs = []
            self._docs_set = set()
            for word_id in self._tf_idf:
                docs_for_word = list(self._tf_idf[word_id].keys())
                self._docs_set = self._docs_set.union(set(docs_for_word))
        self._docs = sorted(list(self._docs_set))

        logger.info(msg="Load matrix from '" + path + "'. " + str(len(self._tf_idf.keys())) + " element(s) loaded.")
        logger.info(msg="Load matrix: tf_idf=" + str(self._tf_idf))
        logger.info(msg="Load matrix: docs=" + str(self._docs))

    def save_matrix(self, path):
        with open(path, "w", encoding='utf8') as f:
            # загружаем матрицу в файл
            # лучше всего использовать для записи и чтения данных struct.pack/unpack
            # пример можно найти в Dictionary.save_dict
            json.dump(self._tf_idf, f)

        logger.info(msg="Save matrix to '" + path + "'. " + str(len(self._tf_idf.keys())) + " element(s) saved.")
        logger.info(msg="Save matrix: tf_idf=" + str(self._tf_idf))
        logger.info(msg="Save matrix: docs=" + str(self._docs))
        logger.info(msg="Save matrix: json=" + json.dumps(self._tf_idf))


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
        # указание на need_revert используется для удобства работы со словарем документов (url <-> doc_id)
        # оно нужно для удобного перехода от doc_id к нормальному представлению имени документа тогда, когда мы будем показывать результаты поиска
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
    matrix = None
    lemmatizer = None

    def __init__(self, index_path):
        ipw = IndexPathWrapper(index_path)

        self.words_dict = Dictionary()
        self.words_dict.load_dict(ipw.get_words_dict_path())

        self.docs_dict = Dictionary(True)
        self.docs_dict.load_dict(ipw.get_docs_dict_path(), True)

        self.matrix = Matrix()
        self.matrix.load_matrix(ipw.get_index_path())

        self.lemmatizer = TextLemmatizer()
