#!/usr/bin/env python
# coding: utf-8

# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import copy
import time
import timeit
from multiprocessing import Pool
from time import gmtime, strftime

from anytree import Node, PreOrderIter

from Util import Util

n = 8
m = 8
DEBUG = True
ONLY_HIGHEST_DEBUG = True
NR_WORKERS = 12
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
        print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))
    # Note: We do not want to manipulate the root - different root-values will be checked in other executions
    # Compute three subsets of the words and of the tree
    bigger_list, equal_list, smaller_list = Util.divide_words(root_comp, words)

    # remove the comparison value at the current node from further consideration
    comps_new_smaller = copy.deepcopy(comps)
    comps_new_equal = copy.deepcopy(comps)
    comps_new_bigger = copy.deepcopy(comps)

    comps_new_smaller.remove(root_comp)
    comps_new_equal.remove(root_comp)
    comps_new_bigger.remove(root_comp)

    # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n and we
    # conduct a comparison between the a_i and a_j which yields  a_i < a_j we can subsequently only
    # investigate the subword a_{i+1} a_{i+2} ... a_n
    if root_comp[0] == 0:
        comps_new_smaller = [c for c in comps_new_smaller if c[0] != 0]
        first_rel_char_smaller = 1
    else:
        first_rel_char_smaller = 0

    if (check_alg(root_node.children[0], smaller_list, comps_new_smaller, [(root_comp, '<')], first_rel_char_smaller)
            and check_alg(root_node.children[1], equal_list, comps_new_equal, [(root_comp, '=')], 0)
            and check_alg(root_node.children[2], bigger_list, comps_new_bigger, [(root_comp, '>')], 0)):
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return root_node
    else:
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return


# Recursively checks all possible decision trees with a given root-value in a Divide and Conquer approach.
# Returns 'True' if a correct decision tree was found.
def check_alg(current_node, words, comps, prev_comps, first_rel_char):
    # If only one word is left from previous comparisons we can immediately decide for this words r-value
    if len(words) <= 1:
        return True

    # If only one distinct r-value is left for all words, we can immediatly take this r-value
    if len(set([w_r for (w, w_r) in words])) == 1:
        return True

    comparisons_left = m - current_node.depth
    subword_length_left = n - first_rel_char

    # If, for a remaining subword of length n' that contains the max. suffix, we know that T(n') is less or equal
    # than the number of comparisons we have left in our subtree, we can return True immediately
    if subword_length_left in Util.knownTn and Util.knownTn[subword_length_left] <= comparisons_left:
        Util.append_known_decision_tree(current_node, first_rel_char, subword_length_left)
        return True

    if not current_node.is_leaf:
        # Divide - here we want to check all possible values for the node (that have not yet been checked)
        for c_new in comps[current_node.last_checked:]:
            if DEBUG and (not ONLY_HIGHEST_DEBUG or current_node.name < 13):
                print("({}, {}) Increasing index {} from {} to {}".format(current_node.root.obj,
                                                                          strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                          current_node.name,
                                                                          current_node.obj, c_new))

            current_node.obj = c_new

            # Compute three subsets of the words and of the tree
            bigger_list, equal_list, smaller_list = Util.divide_words(current_node.obj, words)

            # Compute all comparisons that can be transitively deduced for each possible outcome
            transitive_smaller = Util.compute_transitive_dependencies(prev_comps, (c_new, '<'))
            transitive_equal = Util.compute_transitive_dependencies(prev_comps, (c_new, '='))
            transitive_bigger = Util.compute_transitive_dependencies(prev_comps, (c_new, '>'))

            # remove current comparison and transitively clear comparisons
            # from further consideration
            comps_smaller_new = copy.deepcopy(comps)
            comps_smaller_new.remove(c_new)
            prev_comps_smaller_new = copy.deepcopy(prev_comps)
            prev_comps_smaller_new.append((c_new, '<'))
            for c, res in transitive_smaller:
                prev_comps_smaller_new.append((c, res))

            for c, res in [t for t in transitive_smaller if t[0] in prev_comps_smaller_new]:
                prev_comps_smaller_new.append((c, res))

            comps_equal_new = copy.deepcopy(comps)
            comps_equal_new.remove(c_new)
            prev_comps_equal_new = copy.deepcopy(prev_comps)
            prev_comps_equal_new.append((c_new, '='))
            for c, res in transitive_equal:
                prev_comps_equal_new.append((c, res))

            for c, res in [t for t in transitive_equal if t[0] in prev_comps_equal_new]:
                prev_comps_equal_new.append((c, res))

            comps_bigger_new = copy.deepcopy(comps)
            comps_bigger_new.remove(c_new)
            prev_comps_bigger_new = copy.deepcopy(prev_comps)
            prev_comps_bigger_new.append((c_new, '>'))
            for c, res in transitive_bigger:
                prev_comps_bigger_new.append((c, res))

            for c, res in [t for t in transitive_bigger if t[0] in prev_comps_bigger_new]:
                prev_comps_bigger_new.append((c, res))

            # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n
            # and we conduct a comparison between the a_i and a_{i+1} which yields  a_i < a_{i+1} we can
            # subsequently only investigate the subword a_{i+1} a_{i+2} ... a_n
            comps_smaller_new, first_rel_char_smaller = Util.filter_comps_for_relevant_suffix(comps_smaller_new,
                                                                                              first_rel_char,
                                                                                              prev_comps_smaller_new)

            comps_equal_new, first_rel_char_equal = Util.filter_comps_for_relevant_suffix(comps_equal_new,
                                                                                          first_rel_char,
                                                                                          prev_comps_equal_new)

            comps_bigger_new, first_rel_char_bigger = Util.filter_comps_for_relevant_suffix(comps_bigger_new,
                                                                                            first_rel_char,
                                                                                            prev_comps_bigger_new)

            if (check_alg(current_node.children[0], smaller_list, comps_smaller_new, prev_comps_smaller_new,
                          first_rel_char_smaller) and
                    check_alg(current_node.children[1], equal_list, comps_equal_new, prev_comps_equal_new,
                              first_rel_char_equal) and
                    check_alg(current_node.children[2], bigger_list, comps_bigger_new, prev_comps_bigger_new,
                              first_rel_char_bigger)):
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
        if len(set([wwms[1] for wwms in words])) > 1:
            # Found two distinct r-values here -> current decision tree can not be legal
            return False
        return True


words_with_max_suffix = MY_UTIL.generate_all_word_with_max_suffix()
print("Need to find Algorithm for {} interesting words".format(len(words_with_max_suffix)))

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
