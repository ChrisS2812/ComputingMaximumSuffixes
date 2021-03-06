#!/usr/bin/env python
# coding: utf-8

import multiprocessing
# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import time
import timeit
from multiprocessing import Pool
from time import gmtime, strftime

from anytree import Node, PreOrderIter

from Util import Util

n = 6
m = 6
DEBUG = True
ONLY_HIGHEST_DEBUG = True
NR_WORKERS = 4
MY_UTIL = Util(n, m)

# Generates an initial decision tree for M comparisons with given root value
# Anytree helps navigating, manipulating and printing the tree (i.e. finding children, parents etc.)
def generate_algorithm(root_value):
    alg = []
    current_index = 0
    for ga_i in range(m + 1):
        if ga_i == 0:
            # Root Node
            root_node = Node(current_index, obj=root_value)
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

                for pair in MY_UTIL.comp_pairs:
                    if pair not in parent_values:
                        alg.append(Node(current_index, obj=pair, last_checked=0, parent=parent))
                        current_index += 1
                        break
    return alg[0]


# Preparation step for check_alg: Loads existent algorithm state for given root comparison value if it exists,
# else it generates a first sensible algorithm state before calling check_alg
def check_alg_for_root_comp(root_comp, words, comps):
    if MY_UTIL.is_already_finished(root_comp):
        return MY_UTIL.load_alg_from_checkpoint(root_comp)
    root_node = MY_UTIL.load_alg_from_checkpoint(root_comp)
    if root_node is None:
        root_node = generate_algorithm(root_comp)

    if DEBUG:
        if NR_WORKERS > 1:
            print("({}, Thread {}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), multiprocessing.current_process().name,
                                                                                   root_comp))
        else:
            print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))
    # Note: We do not want to manipulate the root - different root-values will be checked in other executions
    # Compute three subsets of the words and of the tree
    bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(root_comp, words)
    comps_smaller = [c for c in comps if c != root_comp]
    comps_equal = [c for c in comps if c != root_comp]
    comps_bigger = [c for c in comps if c != root_comp]

    # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n and we
    # conduct a comparison between the a_i and a_j which yields  a_i < a_j we can subsequently only
    # investigate the subword a_{i+1} a_{i+2} ... a_n
    if root_comp[0] == 0:
        comps_smaller = [c for c in comps_smaller if c[0] != 0] + [c for c in comps_smaller if c[0] == 0]
        first_rel_char_smaller = 1
    else:
        first_rel_char_smaller = 0

    if (check_alg(root_node.children[0], smaller_list, comps_smaller, first_rel_char_smaller)
        and check_alg(root_node.children[1], equal_list, comps_equal, 0)
        and check_alg(root_node.children[2], bigger_list, comps_bigger, 0)):
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return root_node
    else:
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return


# Recursively checks all possible decision trees with a given root-value in a Divide and Conquer approach.
# Returns 'True' if a correct decision tree was found.
def check_alg(current_node, words, comps, first_rel_char):
    # If only one word is left from previous comparisons we can immediately decide for this words r-value
    if not comps or len([w for w in words if len(w) > 0]) <= 1:
        return True

    if current_node.depth < m-1:
        # Divide - here we want to check all possible values for the node (that have not yet been checked)
        for c_new in comps[current_node.last_checked:]:
            if DEBUG and (not ONLY_HIGHEST_DEBUG or current_node.name < 4):
                print("({}, {}) Increasing index {} from {} to {}".format(current_node.root.obj,
                                                                          strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                          current_node.name,
                                                                          current_node.obj, c_new))

            current_node.obj = c_new

            bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(current_node.obj, words)

            # prepare list of remaining comparisons for each child
            comps_smaller = [c for c in comps if c != c_new]
            first_rel_char_smaller = first_rel_char
            if c_new[0] == first_rel_char:
                comps_smaller = [c for c in comps_smaller if c[0] != first_rel_char] + [c for c in comps_smaller if c[0] == first_rel_char]
                first_rel_char_smaller += 1
            comps_equal = [c for c in comps if c != c_new]
            comps_bigger = [c for c in comps if c != c_new]

            if (check_alg(current_node.children[0], smaller_list, comps_smaller, first_rel_char_smaller) and
                    check_alg(current_node.children[1], equal_list, comps_equal, first_rel_char) and
                    check_alg(current_node.children[2], bigger_list, comps_bigger, first_rel_char)):
                return True
            else:
                # reset last_checked of all vertices below the current one as we are updating this ones comparison value
                for node in PreOrderIter(current_node):
                    # do not change checked value at root
                    if node.name != current_node.name:
                        node.last_checked = 0
                current_node.last_checked += 1
                MY_UTIL.save_current_graph(current_node.root)
        return False

    else:
        # Conquer
        nonempty_lists = [l for l in words if len(l) > 0]
        nr_nonempty = len(nonempty_lists)

        if nr_nonempty < 2:
            return True

        if nr_nonempty > 3:
            return False

        for c in comps:
            i, j = c
            results = []
            for l in nonempty_lists:
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
                for k in range(nr_nonempty):
                    for word in nonempty_lists[k]:
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
                    current_node.obj = c
                    return True
        return False


words_with_max_suffix = MY_UTIL.generate_all_words()

start = 0  # measure running time

working_algs = []

runtime_start = time.time()
if NR_WORKERS > 1:
    # worker pool - each worker is responsible for a single root value
    workers = Pool(processes=NR_WORKERS)
    try:
        results = []
        for comp in MY_UTIL.comp_pairs:
            start = timeit.default_timer()  # measure running time
            r = workers.apply_async(check_alg_for_root_comp, (comp, words_with_max_suffix, MY_UTIL.comp_pairs),
                                    callback=MY_UTIL.save_algorithm)
            results.append(r)
        for r in results:
            r.wait()
    except (KeyboardInterrupt, SystemExit):
        print("except: attempting to close pool")
        workers.terminate()
        print("pool successfully closed")

    finally:
        print("finally: attempting to close pool")
        workers.terminate()
        print("pool successfully closed")

else:
    for comp in MY_UTIL.comp_pairs:
        working_algs.append(check_alg_for_root_comp(comp, words_with_max_suffix, MY_UTIL.comp_pairs))

print("Runtime: {}s".format(time.time() - runtime_start))

for i, root in enumerate(working_algs):
    MY_UTIL.save_algorithm(root)
