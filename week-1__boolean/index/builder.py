#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import json
import logging
import sys
from index.wrapper import Dictionary
from index.wrapper import IndexPathWrapper
from index.wrapper import Matrix
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
    matrix = None

    def __init__(self, path):
        self.ipw = IndexPathWrapper(path)
        self.docs_dict = Dictionary(True)
        self.words_dict = Dictionary(True)
        self.matrix = Matrix()
        self.lemmatizer = TextLemmatizer()

    def build_index(self):
        logger.info(msg="Build index")
        # считываем исходный файл
        # каждая строка - валидный json, в котором точно есть поля url и content
        with open(self.ipw.get_raw_docs_path(), "r") as in_file:
            doc_id = 0
            word_id = 1

            for line in in_file:
                doc_id = doc_id + 1
                jo = json.loads(line, 'utf-8')

                # нормализуем текст
                text = jo["content"]
                # 1. Объединение цифр в один токен в случае, если разряды разделялись дополнительным пробелом.
                # Пример: стандартная запись числа "10 000". После этого этапа 2 терма превратятся в один: "10000"
                text = TextNormalizer.join_numbers(text)
                # 2. Удаляем все знаки пунктуации. Мы используем упрощенную индексацию, поэтому пунктуация нам не нужна
                text = TextNormalizer.clean_out_punct(text)
                # 3. Понижаем регистр текста
                text = TextNormalizer.lower_case(text)
                # 4. Разбиваем текст на термы
                terms = TextNormalizer.split(text)
                # 5. Лемматизация
                lemmas = [self.lemmatizer.lemmatize(term) for term in terms]
                # Некоторые леммы могут встречаться в документе несколько раз. Для нас это лишняя информация => уникуем леммы
                lemmas_unique = set(lemmas)

                # Заполняем словарь для документов: отображение урла на doc_id
                self.docs_dict.add_elem(str(jo["url"]), doc_id)

                for lemma in lemmas_unique:
                    # Пытаемся добавить очередную лемму в словарь слов
                    new_id = self.words_dict.add_elem(lemma, word_id)
                    if new_id < word_id:
                        # в словаре уже есть такая лемма
                        pass
                    else:
                        # это новая лемма, она получает уникальный word_id. Следующей нужен будет другой id
                        word_id = word_id+1

                    # Сохраняем информацию о том, что эта лемма есть в этом документе в матрицу инцидентности
                    self.matrix.activate(new_id, doc_id)

        logger.info(str(self.docs_dict.dictionary_size) + " doc(s), " + str(self.words_dict.dictionary_size) + " word(s)")

        self.words_dict.save_dict(self.ipw.get_words_dict_path())
        self.docs_dict.save_dict(self.ipw.get_docs_dict_path())
        self.matrix.save_matrix(self.ipw.get_index_path())


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        logger.fatal(msg="Incorrect input")
        exit(1)
    IndexBuilder(sys.argv[1]).build_index()
