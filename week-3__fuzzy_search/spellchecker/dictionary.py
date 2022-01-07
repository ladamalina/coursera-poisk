#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import re
import logging
from collections import Counter

logging.basicConfig(
    format='%(levelname)s %(asctime)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('dictionary')


def soundex_en(name):
    # Initialize the end result with the first letter of the input string
    soundex_result = name[0].upper()

    # Remove all instances of h's and w's, since letters with like values
    # are all treated similar when they are adjacent or separated only by
    # h's and w's. This will make our later regex operations simpler.
    input_string = re.sub('[hw]', '', name, flags=re.I)

    # Replace all valued consonants with their respective values. Adjacent
    # valued consonants are treated as one consonant.
    input_string = re.sub('[bfpv]+', '1', input_string, flags=re.I)
    input_string = re.sub('[cgjkqsxz]+', '2', input_string, flags=re.I)
    input_string = re.sub('[dt]+', '3', input_string, flags=re.I)
    input_string = re.sub('l+', '4', input_string, flags=re.I)
    input_string = re.sub('[mn]+', '5', input_string, flags=re.I)
    input_string = re.sub('r+', '6', input_string, flags=re.I)

    # This transformed string still contains the first letter, so remove
    # its value from the string.
    input_string = input_string[1:]

    # Now remove all vowels and y's from the string.
    input_string = re.sub('[aeiouy]', '', input_string, flags=re.I)

    # Take the first 3 digits of the transformed string and append them to the result
    soundex_result += input_string[0:3]

    # Soundex results are supposed to have an opening letter followed by three digits.
    # If there are less than 4 characters total, append with zeros until there are 4.
    if len(soundex_result) < 4:
        soundex_result += '0' * (4 - len(soundex_result))

    return soundex_result


ru_chars = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def soundex_ru(name):
    """
    The Soundex algorithm assigns a 1-letter + 3-digit code to strings,
    the intention being that strings pronounced the same but spelled
    differently have identical encodings; words pronounced similarly
    should have similar encodings.
    """

    soundex_result = name[0].upper()

    name_repr = re.sub('[ьъ]', '', name, flags=re.I)

    name_repr = re.sub('[бпфв]+', '1', name_repr, flags=re.I)
    name_repr = re.sub('[сцзкгх]+', '2', name_repr, flags=re.I)
    name_repr = re.sub('[дт]+', '3', name_repr, flags=re.I)
    name_repr = re.sub('л+', '4', name_repr, flags=re.I)
    name_repr = re.sub('[мн]+', '5', name_repr, flags=re.I)
    name_repr = re.sub('р+', '6', name_repr, flags=re.I)

    name_repr = name_repr[1:]

    numeric_filter = filter(str.isdigit, name_repr)
    name_repr = "".join(numeric_filter)

    soundex_result += name_repr[0:3]

    # Soundex results are supposed to have an opening letter followed by three digits.
    # If there are less than 4 characters total, append with zeros until there are 4.
    if len(soundex_result) < 4:
        soundex_result += '0' * (4 - len(soundex_result))

    return soundex_result


class Dictionary:
    """
    Класс словаря. Он используется для построения словаря из корпуса запросов,
    хранения слов и частоты их появления. Этот словарь затем будет использоваться
    спеллчекером.
    """
    def __init__(self, file_name=""):
        self.soundex_map = {}
        if not file_name:
            self.words = dict()
        else:
            self.load(file_name)

    def load(self, file_name):
        """Загрузка словаря из файла.

        Словарь хранится в файле в простом несжатом формате:
        ...
        слово \t его частоста
        ...

        На  кажой строке хранится одно слово и частоста встречаемости в корпусе, разделенные
        символом табуляции.

        Параметры:
        - file_name: Имя файла, из которого будет загружен словарь.

        Возвращаемое значение:
        - Данный метод ничего не возвращает.
        """
        self.words = dict()
        with open(file_name, 'rt', encoding='utf-8') as fd:
            for line in fd:
                (word, count) = line.strip('\n').split('\t')
                self.words[word] = int(count)
                self.put_soundex(word)

    def save(self, file_name):
        """Сохранение словаря в файл.

        Параметры:
        - file_name: Имя файла, в который будет сохранен словарь.

        Возвращаемое значение:
        - Данный метод ничего не возвращает.
        """
        with open(file_name, 'wt', encoding='utf-8') as fd:
            for word, count in self.words.items():
                fd.write("{}\t{}\n".format(word, count))

    @staticmethod
    def get_words(line):
        """Получить список слов из строки запроса.

        Данная функция разделяет строку по пробелам.
        Все символы пунктуации и другие символы, не являющиеся буквами или дефисом
        должны быть удалены.
        Все слова приводятся к нижнему регистру.
        Все слова с числами удаляются.

        Пример:
        по-отечески похлопал - ['по-отечески', 'похлопал']

        Вход:
        - line: строка запроса

        Возврат:
        - Список слов запроса, удовлетворяющих критериям.
        """
        import re
        expr = "^[\\w\\d\\-]+$"

        line2 = line.replace("+", " ")
        words = [_.strip().lower() for _ in line2.split()]
        words2 = []
        for w in words:
            new_word = ""
            for ch in w:
                if bool(re.match(expr, ch)):
                    new_word += ch
            if len(new_word):
                words2.append(new_word)

        expr2 = ".*[\\d]+.*"
        words3 = [_ for _ in words2 if not bool(re.match(expr2, _))]

        # logger.info("get_words: line=[{}]".format(line))
        # logger.info("get_words: words={}".format(words3))

        return words3

    def build(self, file_name, threshold=0):
        """Построить словарь из файла с запросами.

        Данная функция строит словарь из корпуса запросов, которые сохранены в файле
        file_name. Если threshold не равен 0, то в слове должны хранится только слова, которые
        встретились в корпусе минимум threshold раз. Это позволяет нам фильтровать слова, написанные
        с ошибками.

        Вход:
        - file_name: имя файла с запросами
        - threshold: опциональный параметр. Если не равен 0, то нужно оставить только те слова,
            которые встречались минимум threshold раз.

        Возврат:
        - Данная функция ничего не возвращает. Словарь должен быть сохранен как self.words.
        """
        from collections import defaultdict
        words_w_tres = defaultdict(int)
        with open(file_name, "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                words_in_line = self.get_words(line)
                for w in words_in_line:
                    words_w_tres[w] += 1

        if threshold > 0:
            self.words = {_: words_w_tres[_] for _ in words_w_tres if words_w_tres[_] >= threshold}
        else:
            self.words = words_w_tres

        for w in self.words:
            self.put_soundex(w)

        # logger.info("build: file_name={}, threshold={}, words={}, len(words)={}"
        #             .format(file_name, threshold, self.words, len(self.words)))

    def get(self, word):
        """Возвратить частоту слова

        Данная функция возвращает частоту, с которой слово встречалось в корпусе. Если слово не
        встречалось, то необходимо возвратить 0.

        Вход:
        - word: слово

        Возврат:
        - Частота слова в словаре или 0, если слово не встречалось.
        """
        if word in self.words:
            return self.words[word]
        else:
            return 0

    def size(self):
        """Размер словаря.

        Возврат:
        - Размер словаря.
        """
        return len(self.words)

    @staticmethod
    def soundex(word):
        """Возвратить soundex-код слова.

        Данная функция кодирует переданное слово в код soundex. Функция должна работать как для русских,
        так и для английских слов.

        Вход:
        - word: слово

        Возврат:
        - Код soundex для переданного слова.
        """
        if word[0].lower() in ru_chars:
            res = soundex_ru(word)
        else:
            res = soundex_en(word)

        return res

    def put_soundex(self, word):
        word_soundex = self.soundex(word)
        if word_soundex not in self.soundex_map:
            self.soundex_map[word_soundex] = set()
        self.soundex_map[word_soundex].add(word)
