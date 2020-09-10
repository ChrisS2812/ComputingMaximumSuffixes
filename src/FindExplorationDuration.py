import itertools
from pprint import pprint

import networkx as nx

from Util import Util

n = 8
m = 8
UTIL = Util(n, m)

tree = UTIL.load_fuzzy_tree(n)

all_words = itertools.product(range(n), repeat=n)
already_seen_comps = {}
nr_comparisons_count = {}

for i, word in enumerate(all_words):
    if i % 100000 == 0:
        print("{} %".format(i / n**n * 100))

    comparisons = ""
    for i in range(n):
        for j in range(i + 1, n):
            c1 = word[i]
            c2 = word[j]
            if c1 < c2:
                comparisons += "<"
            elif c1 > c2:
                comparisons += ">"
            else:
                comparisons += "="
    if comparisons not in already_seen_comps:
        already_seen_comps[comparisons] = 1
        count = 0
        current_node = tree.root
        G = nx.DiGraph()
        G.add_nodes_from(range(n))

        while isinstance(current_node.obj, list):
            if nx.is_weakly_connected(G):
                if not count in nr_comparisons_count:
                    nr_comparisons_count[count] = 1
                else:
                    nr_comparisons_count[count] += 1
                break
            count += 1
            i1, i2 = current_node.obj
            if word[i1] < word[i2]:
                G.add_edge(i1, i2)
                current_node = current_node.children[0]
            elif word[i1] == word[i2]:
                G.add_edge(i2, i1)
                G.add_edge(i1, i2)
                current_node = current_node.children[1]
            else:
                G.add_edge(i2, i1)
                current_node = current_node.children[2]

pprint(nr_comparisons_count)