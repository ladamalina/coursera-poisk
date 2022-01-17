"""
Пусть у нас есть запрос q "смотреть видео с котиками" и документ d "Котики в дикой природе. Все смешные видео здесь."
Мы знаем, что терм "смотреть" в нашей коллекции встретился 215 раз в документах релевантных запросу,
а всего этот терм содержит 13102 документов. "Котики" в нашей коллекции встретился 22 раза в документах,
релевантных данному запросу, и 910 документов содержат этот терм. Терм "видео" встретился 115 раз
в релевантных документах, и всего в 9810 документах коллекции. Общее количество документов в коллекции 100000,
из них 710 являются релевантными данному запросу q. Посчитайте значение RSV используя бинарную модель независимости.
"""

import math
from dataclasses import dataclass

N = 100000
S = 710


@dataclass
class Term:
    term: str
    s: int
    n: int

    @property
    def pi(self) -> float:
        return self.s / S

    @property
    def ri(self) -> float:
        return (self.n - self.s) / (N-S)

    @property
    def ci(self) -> float:
        return math.log(
            (self.pi*(1-self.ri))
            /
            (self.ri*(1-self.pi))
        )

    def __repr__(self) -> str:
        return f"<Term {self.term=}, {self.s=}, {self.n=}, {self.pi=}, {self.ri=}, {self.ci=}>"


def rsv(terms: list) -> float:
    return sum([_.ci for _ in terms])


if __name__ == "__main__":
    terms = [
        Term("смотреть", 215, 13102),
        Term("Котики", 22, 910),
        Term("видео", 115, 9810),
    ]
    for t in terms:
        print(t)
    print(rsv(terms))
