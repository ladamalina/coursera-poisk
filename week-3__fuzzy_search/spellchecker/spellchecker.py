#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import logging
import numpy
from .dictionary import Dictionary
from collections import defaultdict
from difflib import ndiff

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('spellchecker')


def ld(s, t):
    if s == "":
        return len(t)
    if t == "":
        return len(s)
    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1

    res = min([ld(s[:-1], t) + 1,
               ld(s, t[:-1]) + 1,
               ld(s[:-1], t[:-1]) + cost])

    return res


def levenshtein_distance(str1, str2, ):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else:
            counter[edit_code] += 1
    distance += max(counter.values())
    return distance

class Spellchecker:
    """ Класс спеллчекера.
    В нем реализованы функции поиска кандидатов исправлений для слов запроса.
    """
    def __init__(self, arg):
        if isinstance(arg, str):
            self.dictionary = Dictionary(arg)
        elif isinstance(arg, Dictionary):
            self.dictionary = arg
        else:
            self.dictionary = Dictionary()

        self.soundex_index = self.build_soundex_index()

    def build_soundex_index(self):
        """Строит индекс между кодами soundex и словами словаря.

        Для каждого слова из словаря строится код soundex и затем слово добавляется в список,
        соответсвующий этому коду.

        код soundex -> [слово1, слово2, ...]

        Возвращаемое значение:
        - Данный метод ничего не возвращает.
        """
        index = defaultdict(list)
        for word, _ in self.dictionary.words.items():
            index[Dictionary.soundex(word)].append(word)

        return dict(index)

    @staticmethod
    def levenshtein_distance(word1, word2):
        """Расстояние Левенштейна

        Рассчитывает расстояние Левенштейна между словами с операциями вставки, удаления и замены символов.
        Вес каждой операции равен 1.

        Параметры:
        - word1: первое слово
        - word2: второе слово

        Возвращаемое значение:
        - Расстояние между словами word1 и word2.
        """
        # return ld(word1, word2)
        return levenshtein_distance(word1, word2)

    def is_correct(self, word):
        """Слово есть в словаре

        Параметры:
        - word: слово для проверки

        Возвращаемое значение:
        - True если слово есть в словаре, иначе False
        """
        return self.dictionary.get(word) != 0

    def get_candidates(self, word, max_distance=3):
        """Поиск списка кандидатов для исправления слова

        Возвращает список кандидатов, отсортированных в порядке убывания частоты встречаемости слова в корпусе.
        Таким образом, мы будем для исправления отдавать наиболее часто встречаемы словам в случае равных
        расстояний редактирования.

        В данном методе поиск кандидатов осуществляется перебором всех возможножных вариантов из словаря.

        Параметры:
        - word: слово для исправления
        - max_distance: опциональный параметр, задает допустимое максимальное число исправлений для кандидатов.

        Возвращаемое значение:
        - Список слов кандидатов с минимальным расстоянием редактирования, отсортированных в порядке убывания
        частоты в корпусе.
        """

        candidates_thres = []
        min_distance_found = float("inf")
        for candidate in self.dictionary.words:
            distance = self.levenshtein_distance(word, candidate)
            if distance > max_distance:
                continue
            if distance < min_distance_found:
                min_distance_found = distance
                candidates_thres = []
            elif distance > min_distance_found:
                continue
            candidates_thres.append(tuple([candidate, distance, self.dictionary.words[candidate]]))
        candidates_thres = sorted(candidates_thres,
                                  key=lambda x: tuple([x[1], -1*x[2]])
                                  )
        # logger.info("get_candidates: word={}, min_distance_found={}, candidates_thres={}"
        #             .format(word, min_distance_found, candidates_thres))
        candidates = [_[0] for _ in candidates_thres]

        return candidates

    def get_candidates_fast(self, word, max_distance=3):
        """Быстрый поиск списка кандидатов для исправления слова

        Предыдущий метод работает очень долго - нужно посчитать расстояние между словом и всеми словами из словаря.
        Для того, чтобы сократить список слов для перебора мы будем считать расстояние только между словами,
        имеющими такой же код soundex как и у проверяемого слова.

        Параметры:
        - word: слово для исправления
        - max_distance: опциональный параметр, задает допустимое максимальное число исправлений для кандидатов.

        Возвращаемое значение:
        - Список слов кандидатов с минимальным расстоянием редактирования, отсортированных в порядке убывания
        частоты в корпусе.
        """
        word_soundex = self.dictionary.soundex(word)
        if word_soundex not in self.dictionary.soundex_map:
            return []

        candidates_by_soundex = self.dictionary.soundex_map[word_soundex]
        # logger.info("get_candidates_fast: word={}, candidates_by_soundex={}".format(word, candidates_by_soundex))

        candidates_thres = []
        min_distance_found = float("inf")
        for candidate in candidates_by_soundex:
            distance = self.levenshtein_distance(word, candidate)
            if distance > max_distance:
                continue
            if distance < min_distance_found:
                min_distance_found = distance
                candidates_thres = []
            elif distance > min_distance_found:
                continue
            candidates_thres.append(tuple([candidate, distance, self.dictionary.words[candidate]]))
        candidates_thres = sorted(candidates_thres,
                                  key=lambda x: tuple([x[1], -1 * x[2]])
                                  )
        # logger.info("get_candidates: word={}, min_distance_found={}, candidates_thres={}"
        #             .format(word, min_distance_found, candidates_thres))
        candidates = [_[0] for _ in candidates_thres]

        return candidates

