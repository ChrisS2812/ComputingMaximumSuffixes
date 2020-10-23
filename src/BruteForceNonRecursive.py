#!/usr/bin/env python
# coding: utf-8
import itertools
import statistics
# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import time
from cmath import sqrt
from time import gmtime, strftime

import random
from anytree import Node
from bitarray._bitarray import bitarray

from Util import Util

n = 5
m = 5
DEBUG = True
MY_UTIL = Util(n, m)

# define how many comparisons are allowed that do not extend the underlying dependency graph
max_m = int((4 * n - 5) / 3)
max_non_endogeneous = max_m - n + 1

ALL_COMPS = MY_UTIL.comp_pairs
NR_COMPS = len(ALL_COMPS)

words = MY_UTIL.generate_all_words()
words_shuffled = list(itertools.chain.from_iterable(words))
random.shuffle(words_shuffled)

inner_node_offset = 0
for i in range(m-1):
    inner_node_offset += 3 ** i

critical_words = None
NR_COMP_EVALS = 0

# Generates an initial decision tree for M comparisons with given root value
# Anytree helps navigating, manipulating and printing the tree (i.e. finding children, parents etc.)
def generate_algorithm(root_value):
    alg = []
    current_index = 0
    for ga_i in range(m+1):
        if ga_i == 0:
            # Root Node
            root_c = NR_COMPS * bitarray('1')
            rho_min = 0
            if root_value[0] == 0:
                rho_min = 1
            root_node = Node(current_index, obj=root_value, c=root_c, rho_min=rho_min)
            alg.append(root_node)
            current_index += 1
        elif ga_i == m:
            # Leaf Nodes
            for ga_j in range(3 ** m):
                parent = alg[(current_index - 1) // 3]
                alg.append(Node(current_index, obj="", parent=parent))
                current_index += 1
        else:
            for ga_j in range(3 ** ga_i):
                parent = alg[(current_index - 1) // 3]
                parent_index = current_index
                parent_values = []
                # Collect all values of (grand-)parents of the current node
                while parent_index != 0:
                    parent_index = (parent_index - 1) // 3
                    parent_values.append(alg[parent_index].obj)

                for i in range(NR_COMPS):
                    if ALL_COMPS[i] not in parent_values:
                        alg.append(Node(current_index, obj=ALL_COMPS[i], c=None, parent=parent, rho_min=0))
                        current_index += 1
                        break
        for child in alg[0].children:
            update_c(child)
    return alg


# Preparation step for check_alg: Loads existent algorithm state for given root comparison value if it exists,
# else it generates a first sensible algorithm state before calling check_alg
def check_alg_for_root_comp(root_comp):
    global critical_words
    alg = generate_algorithm(root_comp)

    if DEBUG:
        print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))

    while True:
        result = check_valid(alg)
        if isinstance(result, bool):
            if critical_words is None:
                return alg
            else:
                critical_words = None
        else:
            if not generate_next(result):
                return

def check_valid(alg):
    global critical_words, NR_COMP_EVALS
    if critical_words:
        words = critical_words
    else:
        words = words_shuffled

    root = alg[0]
    hitting_sets = [[[] for _ in range(3)] for _ in range(len(root.leaves))]
    r_vals = [[] for _ in range(len(root.leaves))]
    for w in words:
        current_node = root
        while not current_node.depth == m-1:
            i1, i2 = current_node.obj
            c1 = w[i1]
            c2 = w[i2]
            NR_COMP_EVALS += 1
            if c1 < c2:
                current_node = current_node.children[0]
            elif c1 == c2:
                current_node = current_node.children[1]
            else:
                current_node = current_node.children[2]
        r = Util.max_suffix_duval(w)
        current_index = current_node.name - inner_node_offset
        if r not in r_vals[current_index]:
            if len(r_vals[current_index]) == 3:
                critical_words = list(itertools.chain.from_iterable(hitting_sets[current_index]))
                critical_words.append(w)
                return current_node.path
            r_vals[current_index].append(r)
        hitting_sets[current_index][r_vals[current_index].index(r)].append(w)

    for nr_hs in [3,2]:
        for hs in [hs for i, hs in enumerate(hitting_sets) if len(r_vals[i]) == nr_hs]:
            found_valid = False
            current_index = hitting_sets.index(hs) + inner_node_offset
            current_node = alg[current_index]
            for c_index in [i for i, bit in enumerate(current_node.c) if bit]:
                i, j = ALL_COMPS[c_index]
                results = []
                for l in [h for h in hs if len(h) > 0]:
                    if l[0][i] < l[0][j]:
                        results.append("<")
                    elif l[0][i] == l[0][j]:
                        results.append("=")
                    else:
                        results.append(">")
                if len(results) > len(set(results)):
                    continue
                else:
                    final_results = [set(r) for r in results]
                    for k in range(nr_hs):
                        for word in hs[k]:
                            NR_COMP_EVALS += 1
                            if word[i] < word[j]:
                                final_results[k].add("<")
                            elif word[i] == word[j]:
                                final_results[k].add("=")
                            else:
                                final_results[k].add(">")

                    nr_results = 0
                    for r in final_results:
                        nr_results += len(r)
                    if nr_results > 3:
                        continue
                    else:
                        alg[current_index].obj = ALL_COMPS[c_index]
                        found_valid = True
                        break
            if not found_valid:
                critical_words = list(itertools.chain.from_iterable(hs))
                return alg[current_index].path
    return True

def update_c(root):
    root_c = root.parent.c
    root_comp = root.parent.obj

    this_c = root_c.copy()
    root.rho_min = root.parent.rho_min

    #No comparison twice
    this_c[ALL_COMPS.index(root_comp)] = False

    #No comps outside max suffix
    if root.parent.rho_min > 0 and root == root.parent.children[0]:
        start = 0
        end = 0
        for i in range(root.parent.rho_min):
            end += n-1-i
        this_c[start:end:1] = False
    root.c = this_c

    if root.obj[0] == root.parent.rho_min:
        root.rho_min = root.parent.rho_min + 1

    if root.depth < m-1:
        for child in root.children:
            update_c(child)


def generate_next(result):
    path_index = -2

    while True:
        if result[path_index] == result[path_index].root:
            return False

        comp_index = ALL_COMPS.index(result[path_index].obj)
        if comp_index != NR_COMPS - 1:
            for ci in range(comp_index+1, NR_COMPS):
                if result[path_index].c[ci]:
                    result[path_index].obj = ALL_COMPS[ci]
                    update_c(result[path_index])
                    return True
        result[path_index].obj = ALL_COMPS[0]
        path_index -= 1

runtimes = []
words_with_max_suffix = MY_UTIL.generate_all_words()
for i in range(1):
    start = 0  # measure running time

    working_algs = []

    runtime_start = time.time()
    for comp in MY_UTIL.comp_pairs:
        working_algs.append(check_alg_for_root_comp(comp))

    runtimes.append(time.time() - runtime_start)
    print("Runtime: {}s".format(time.time() - runtime_start))

    for i, alg in enumerate(working_algs):
        if alg is not None:
            MY_UTIL.check_valid(alg[0])
    print("Nr comp. evals. on words: {}".format(NR_COMP_EVALS))
    NR_COMP_EVALS = 0

print("Mean: {}".format(sum(runtimes) / len(runtimes)))
print("Standarddeviation: {}".format(statistics.stdev(runtimes)))
print("Standarderror: {}".format(statistics.stdev(runtimes) / sqrt(10)))
