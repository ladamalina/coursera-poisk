"""
Пусть у нас есть запрос "президент Линкольн". Размер коллекции документов равен 500000.
Терм "президент" сожержится в 40000 документах, а терм "Линкольн" в 300.
Пусть в документе терм "президент" встречается 15 раз, а терм "Линкольн" 25. Отношение dl/avdl равно 0.9.
Коэффициенты k1=1.2, b=0.75, k2=100.
Рассчитайте значение bm25 для данной пары запрос/документ, ответ округлите до сотых.
"""

import math
from dataclasses import dataclass

N = 500000
dl_avdl = 0.9
k1 = 1.2
b = 0.75
k2 = 100


@dataclass
class Term:
    term: str
    tf: int
    docs: int

    @property
    def idf(self) -> float:
        return math.log(N/self.docs)

    @property
    def bm25(self) -> float:
        return self.idf * (
            ((k1 + 1) * self.tf)
            /
            (k1*(1 - b + b * dl_avdl) + self.tf)
        )

    def __repr__(self) -> str:
        return f"<Term {self.term=}, {self.tf=}, {self.idf=}, {self.bm25=}>"


def rsv_bm25(terms: list) -> float:
    return sum([_.bm25 for _ in terms])


if __name__ == "__main__":
    terms = [
        Term("президент", 15, 40000),
        Term("Линкольн", 25, 300),
    ]
    for t in terms:
        print(t)
    print(rsv_bm25(terms))


    terms = [
        Term("президент", 15, 40000),
        Term("Линкольн", 1, 300),
    ]
    for t in terms:
        print(t)
    print(rsv_bm25(terms))


    terms = [
        Term("президент", 1, 40000),
        Term("Линкольн", 25, 300),
    ]
    for t in terms:
        print(t)
    print(rsv_bm25(terms))
