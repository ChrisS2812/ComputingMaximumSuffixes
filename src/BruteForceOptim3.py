#!/usr/bin/env python
# coding: utf-8

import statistics
# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import time
from cmath import sqrt
from multiprocessing import Pool
from time import gmtime, strftime

from anytree import Node

from Util import Util

n = 7
m = 7
DEBUG = True
ONLY_HIGHEST_DEBUG = True

MY_UTIL = Util(n, m)
NR_WORKERS = 1
NR_CALLS = 0

# define how many comparisons are allowed that do not extend the underlying dependency graph
max_m = int((4 * n - 5) / 3)
max_non_endogeneous = max_m - n + 1


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
    root_node = generate_algorithm(root_comp)

    if DEBUG:
        print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))
    # Note: We do not want to manipulate the root - different root-values will be checked in other executions
    # Compute three subsets of the words and of the tree
    bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(root_comp, words)
    comps_smaller = [c for c in comps if c != root_comp]
    comps_equal = [c for c in comps if c != root_comp]
    comps_bigger = [c for c in comps if c != root_comp]
    # union-find datastructure that is used to keep track if the underlying ordering graph is yet weakly connected
    # cc = UF(n)
    # cc.union(root_comp[0], root_comp[1])
    #
    # # graph that keeps track of transitive dependencies
    # G = nx.DiGraph()
    # G.add_nodes_from(range(n))
    #
    # G_smaller = G.copy()
    # G_equal = G.copy()
    # G_bigger = G.copy()
    #
    # G_smaller.add_edge(root_comp[0], root_comp[1])
    # G_equal.add_edge(root_comp[0], root_comp[1])
    # G_equal.add_edge(root_comp[1], root_comp[0])
    # G_bigger.add_edge(root_comp[1], root_comp[0])
    #
    # # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n and we
    # # conduct a comparison between the a_i and a_j which yields  a_i < a_j we can subsequently only
    # # investigate the subword a_{i+1} a_{i+2} ... a_n
    if root_comp[0] == 0:
        comps_smaller = [c for c in comps_smaller if c[0] != 0] + [c for c in comps_smaller if c[0] == 0]
        first_rel_char_smaller = 1
    else:
        first_rel_char_smaller = 0

    if (check_alg(root_node.children[0], smaller_list, comps_smaller, first_rel_char_smaller)
            and check_alg(root_node.children[1], equal_list, comps_equal, 0)
            and check_alg(root_node.children[2], bigger_list, comps_bigger, 0)):
        return root_node
    else:
        return


# Recursively checks all possible decision trees with a given root-value in a Divide and Conquer approach.
# Returns 'True' if a correct decision tree was found.
def check_alg(current_node, words, comps, first_rel_char):
    global NR_CALLS
    NR_CALLS += 1
    # If only one word is left from previous comparisons we can immediately decide for this words r-value
    if not comps or len([w for w in words if len(w) > 0]) <= 1:
        return True
    #
    # comparisons_left = m - current_node.depth
    # exogeneous_comparisons_needed = connected_components.count() - 1
    # if exogeneous_comparisons_needed > comparisons_left:
    #     return False

    # subword_length_left = n - first_rel_char

    # # If, for a remaining subword of length n' that contains the max. suffix, we know that T(n') is less or equal
    # # than the number of comparisons we have left in our subtree, we can return True immediately
    # if subword_length_left in Util.knownTn and Util.knownTn[subword_length_left] <= comparisons_left:
    #     Util.append_known_decision_tree(current_node, first_rel_char, subword_length_left)
    #     return True

    if current_node.depth < m - 1:
        # Divide - here we want to check all possible values for the node (that have not yet been checked)
        for c_new in comps:
            if DEBUG and (not ONLY_HIGHEST_DEBUG or current_node.name < 4):
                print("({}, {}) Increasing index {} from {} to {}".format(current_node.root.obj,
                                                                          strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                          current_node.name,
                                                                          current_node.obj, c_new))

            current_node.obj = c_new

            bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(current_node.obj, words)

            # cc1 = copy.deepcopy(connected_components)
            # cc2 = copy.deepcopy(connected_components)
            # cc3 = copy.deepcopy(connected_components)
            #
            # cc1.union(c_new[0], c_new[1])
            # cc2.union(c_new[0], c_new[1])
            # cc3.union(c_new[0], c_new[1])

            # prepare list of remaining comparions for each child
            comps_smaller = [c for c in comps if c != c_new]
            first_rel_char_smaller = first_rel_char
            if c_new[0] == first_rel_char:
                comps_smaller = [c for c in comps_smaller if c[0] != first_rel_char] + [c for c in comps_smaller if c[0] == first_rel_char]
                first_rel_char_smaller += 1
            comps_equal = [c for c in comps if c != c_new]
            comps_bigger = [c for c in comps if c != c_new]
            #
            # connected_components.union(c_new[0], c_new[1])
            #
            # dep_graph_smaller = dep_graph.copy()
            # dep_graph_equal = dep_graph.copy()
            # dep_graph_bigger = dep_graph.copy()
            #
            # dep_graph_smaller.add_edge(c_new[0], c_new[1])
            # dep_graph_equal.add_edge(c_new[0], c_new[1])
            # dep_graph_equal.add_edge(c_new[1], c_new[0])
            # dep_graph_bigger.add_edge(c_new[1], c_new[0])
            #
            # # find nodes that are smaller/bigger than the character at c_new[0]
            # trans_smaller_bigger = nx.descendants(dep_graph_smaller, c_new[0])
            # trans_smaller_smaller = nx.descendants(dep_graph_smaller.reverse(False), c_new[0])
            # trans_smaller_smaller.add(c_new[0])
            #
            # trans_bigger_bigger = nx.descendants(dep_graph_bigger, c_new[1])
            # trans_bigger_smaller = nx.descendants(dep_graph_bigger.reverse(False), c_new[1])
            # trans_bigger_smaller.add(c_new[1])
            #
            # # check if prefixes can be excluded from further consideration
            # first_rel_char_smaller = first_rel_char
            # first_rel_char_equal = first_rel_char
            # first_rel_char_bigger = first_rel_char
            #
            # while first_rel_char_smaller in trans_smaller_smaller:
            #     comps_smaller = [c for c in comps_smaller if c[0] != first_rel_char_smaller]
            #     first_rel_char_smaller += 1
            #
            # while first_rel_char_bigger in trans_bigger_smaller:
            #     comps_bigger = [c for c in comps_bigger if c[0] != first_rel_char_bigger]
            #     first_rel_char_bigger += 1
            #
            # while True:
            #     if first_rel_char_equal in trans_smaller_smaller and first_rel_char_equal not in trans_bigger_bigger:
            #         comps_equal = [c for c in comps_equal if c[0] != first_rel_char_equal]
            #         first_rel_char_equal += 1
            #
            #     elif first_rel_char_equal in trans_bigger_smaller and first_rel_char_equal not in trans_smaller_bigger:
            #         comps_equal = [c for c in comps_equal if c[0] != first_rel_char_equal]
            #         first_rel_char_equal += 1
            #     else:
            #         break
            #
            # # remove transitively determined dependencies from further consideration
            # for i in trans_smaller_smaller:
            #     for j in trans_smaller_bigger:
            #         if sorted([i, j]) in comps_smaller:
            #             comps_smaller.remove(sorted([i, j]))
            #         if sorted([i, j]) in comps_equal:
            #             comps_equal.remove(sorted([i, j]))
            #
            # for i in trans_bigger_smaller:
            #     for j in trans_bigger_bigger:
            #         if sorted([i, j]) in comps_bigger:
            #             comps_bigger.remove(sorted([i, j]))
            #         if sorted([i, j]) in comps_equal:
            #             comps_equal.remove(sorted([i, j]))

            if (check_alg(current_node.children[0], smaller_list, comps_smaller, first_rel_char_smaller) and
                    check_alg(current_node.children[1], equal_list, comps_equal, first_rel_char) and
                    check_alg(current_node.children[2], bigger_list, comps_bigger, first_rel_char)):
                return True
        return False

    else:
        # Conquer
        nonempty_lists = [l for l in words if len(l) > 0]
        nr_nonempty = len(nonempty_lists)
        if nr_nonempty > 3:
            return False

        for c_new in comps:
            i, j = c_new
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
                    current_node.obj = c_new
                    return True
        return False


runtimes = []
words_with_max_suffix = MY_UTIL.generate_all_words()

for i in range(1):
    working_algs = []
    if NR_WORKERS > 1:
        # worker pool - each worker is responsible for a single root value
        workers = Pool(processes=NR_WORKERS)
        runtime_start = time.time()
        try:
            results = []
            for comp in MY_UTIL.comp_pairs:
                r = workers.apply_async(check_alg_for_root_comp, (comp, words_with_max_suffix, MY_UTIL.comp_pairs),
                                        callback=MY_UTIL.check_valid)
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
        runtimes.append(time.time() - runtime_start)
        print("Runtime: {}s".format(time.time() - runtime_start))
    else:
        runtime_start = time.time()
        for comp in MY_UTIL.comp_pairs:
            working_algs.append(check_alg_for_root_comp(comp, words_with_max_suffix, MY_UTIL.comp_pairs))

        runtimes.append(time.time() - runtime_start)
        print("Runtime: {}s".format(time.time() - runtime_start))
        print("Nr. calls: {}".format(NR_CALLS))
        NR_CALLS = 0

        for i, root in enumerate(working_algs):
            if root is not None:
                MY_UTIL.check_valid(root)

print("Mean: {}".format(sum(runtimes) / len(runtimes)))
print("Standarddeviation: {}".format(statistics.stdev(runtimes)))
print("Standarderror: {}".format(statistics.stdev(runtimes) / sqrt(i)))
