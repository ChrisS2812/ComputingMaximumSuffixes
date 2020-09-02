import itertools
from pprint import pprint

from Util import Util

for n in range(1, 10):
    UTIL = Util(n, -1)
    all_words = itertools.product(range(n), repeat=n)
    distr_table = {i: 0 for i in range(n)}

    for word in all_words:
        distr_table[UTIL.max_suffix_duval(word)] += 1

    for key in distr_table:
        value = distr_table[key]
        distr_table[key] = value / n**n * 100

    print("========================================")
    print("n={}".format(n))
    pprint(distr_table)