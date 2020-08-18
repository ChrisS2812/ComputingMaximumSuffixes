#!/usr/bin/env python
# coding: utf-8

# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import copy
import datetime
import timeit
from multiprocessing import Pool
from time import gmtime, strftime

from anytree import Node, RenderTree
from anytree.exporter import DotExporter

from src.Util import Util

N = 6
M = 5
DEBUG = True
ONLY_HIGHEST_DEBUG = True
NR_WORKERS = 1
MY_UTIL = Util(N, M)

# Compute all possible pairs of indices that can be compared
comp_pairs = []
for i in range(N):
    for j in range(i + 1, N):
        comp_pairs.append([i, j])
print(comp_pairs)


# Generates a decision tree for M comparisons with given root value that fulfils the following rule(s):
# 1. No path contains the same node value twice
#
# Define a tree structure inside a list, each representing a different height of the tree. Anytree helps us
# navigating the tree (i.e. finding children, parents etc.)
def generate_algorithm(root_value):
    alg = []
    current_index = 0
    for ga_i in range(M + 1):
        if ga_i == 0:
            # Root Node
            root = Node(current_index, obj=root_value)
            alg.append(root)
            current_index += 1
        elif ga_i == M:
            # Leaf Nodes
            for ga_j in range(3 ** M):
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

                for pair in comp_pairs:
                    if pair not in parent_values:
                        alg.append(Node(current_index, obj=pair, checked=[], parent=parent))
                        current_index += 1
                        break
    return alg


# Preparation step for check_alg: Loads existent algorithm state for given root comparison value if it exists,
# else it generates a first sensible algorithm state before calling check_alg
def check_alg_for_root_comp(root_comp, words, comps):
    alg = MY_UTIL.load_alg_from_checkpoint(root_comp)
    if alg == -1:
        alg = generate_algorithm(root_comp)

    if DEBUG:
        print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))
    # Note: We do not want to manipulate the root - different root-values will be checked in other executions
    # Compute three subsets of the words and of the tree
    i1, i2 = root_comp
    smaller_list = []
    equal_list = []
    bigger_list = []
    for entry in words:
        curr_word = entry[0]
        if curr_word[i1] < curr_word[i2]:
            smaller_list.append(entry)
        elif curr_word[i1] == curr_word[i2]:
            equal_list.append(entry)
        else:
            bigger_list.append(entry)

    # remove the comparison value at the current node from further consideration
    comps_new_smaller = copy.deepcopy(comps)
    comps_new_equal = copy.deepcopy(comps)
    comps_new_bigger = copy.deepcopy(comps)

    comps_new_smaller.remove(root_comp)
    comps_new_equal.remove(root_comp)
    comps_new_bigger.remove(root_comp)

    # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n and we
    # conduct a comparison between the a_i and a_{i+1} which yields  a_i < a_{i+1} we can subsequently only
    # investigate the subword a_{i+1} a_{i+2} ... a_n
    if root_comp == [0, 1]:
        comps_new_smaller = [c for c in comps_new_smaller if c[0] != 0]

    if (check_alg(alg, 1, smaller_list, comps_new_smaller, [(root_comp, '<')], 1) and
            check_alg(alg, 2, equal_list, comps_new_equal, [(root_comp, '=')], 1) and
            check_alg(alg, 3, bigger_list, comps_new_bigger, [(root_comp, '>')], 1)):
        return alg
    else:
        return


# Recursively checks all possible decision trees with a given root-value in a Divide and Conquer approach.
# Returns 'True' if a correct decision tree was found.
def check_alg(alg, index, words, comps, prev_comps, first_rel_char):
    if len(words) < 1:
        return True

    if not MY_UTIL.is_leaf(index):
        # Divide - here we want to check all possible values for the node (that have not yet been checked)
        for c_new in [c for c in comps if c not in alg[index].checked]:
            if DEBUG and (not ONLY_HIGHEST_DEBUG or index < 4):
                print("({}, {}) Increasing index {} from {} to {}".format(alg[0].obj,
                                                                          strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                          index,
                                                                          alg[index].obj, c_new))

            alg[index].obj = c_new

            # Compute three subsets of the words and of the tree
            i1, i2 = alg[index].obj
            smaller_list = []
            equal_list = []
            bigger_list = []
            for entry in words:
                curr_word = entry[0]
                if curr_word[i1] < curr_word[i2]:
                    smaller_list.append(entry)
                elif curr_word[i1] == curr_word[i2]:
                    equal_list.append(entry)
                else:
                    bigger_list.append(entry)

            # Compute all comparisons that can be transitively deduced for each possible outcome
            transitive_smaller = MY_UTIL.compute_transitive_dependencies(prev_comps, (c_new, '<'))
            transitive_equal = MY_UTIL.compute_transitive_dependencies(prev_comps, (c_new, '='))
            transitive_bigger = MY_UTIL.compute_transitive_dependencies(prev_comps, (c_new, '>'))

            # remove current comparison and transitively clear comparisons
            # from further consideration
            comps_smaller_new = copy.deepcopy(comps)
            prev_comps_smaller_new = copy.deepcopy(prev_comps)
            prev_comps_smaller_new.append((c_new, '<'))
            comps_smaller_new.remove(c_new)
            for c, res in [t for t in transitive_smaller if t[0] in comps]:
                comps_smaller_new.remove(c)
                prev_comps_smaller_new.append((c, res))

            comps_equal_new = copy.deepcopy(comps)
            comps_equal_new.remove(c_new)
            prev_comps_equal_new = copy.deepcopy(prev_comps)
            prev_comps_equal_new.append((c_new, '='))
            for c, res in [t for t in transitive_equal if t[0] in comps]:
                comps_equal_new.remove(c)
                prev_comps_equal_new.append((c, res))

            comps_bigger_new = copy.deepcopy(comps)
            comps_bigger_new.remove(c_new)
            prev_comps_bigger_new = copy.deepcopy(prev_comps)
            prev_comps_bigger_new.append((c_new, '>'))
            for c, res in [t for t in transitive_bigger if t[0] in comps]:
                comps_bigger_new.remove(c)
                prev_comps_bigger_new.append((c, res))

            # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n
            # and we conduct a comparison between the a_i and a_{i+1} which yields  a_i < a_{i+1} we can
            # subsequently only investigate the subword a_{i+1} a_{i+2} ... a_n
            if c_new == (first_rel_char, first_rel_char + 1):
                comps_smaller_new = [c for c in comps_smaller_new if c[0] != first_rel_char]

            if (check_alg(alg, index * 3 + 1, smaller_list, comps_smaller_new, prev_comps_smaller_new,
                          first_rel_char + 1) and
                    check_alg(alg, index * 3 + 2, equal_list, comps_equal_new, prev_comps_equal_new,
                              first_rel_char) and
                    check_alg(alg, index * 3 + 3, bigger_list, comps_bigger_new, prev_comps_bigger_new,
                              first_rel_char)):
                alg[index].checked = []
                MY_UTIL.save_current_graph(alg[0])
                return True
            else:
                alg[index].checked.append(c_new)
                MY_UTIL.save_current_graph(alg[0])
        alg[index].checked = []
        return False

    else:
        # Conquer
        if len(set([wwms[1] for wwms in words])) > 1:
            # Found two distinct r-values here -> current decision tree can not be legal
            return False
        return True


# Helping function that stop the workers early when a solution was found
working_alg = []


def check_result(return_alg):
    global working_alg
    if not working_alg and return_alg is not None:
        working_alg = return_alg
        workers.terminate()


words_with_max_suffix = MY_UTIL.generate_all_word_with_max_suffix()
print("Need to find Algorithm for {} interesting words".format(len(words_with_max_suffix)))

start = 0  # measure running time

if NR_WORKERS > 1:
    # worker pool - each worker is responsible for a single root value
    workers = Pool(processes=NR_WORKERS)
    try:
        results = []
        for comp in comp_pairs:
            start = timeit.default_timer()  # measure running time
            r = workers.apply_async(check_alg_for_root_comp, (comp, words_with_max_suffix, comp_pairs),
                                    callback=check_result)
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
    for comp in comp_pairs:
        start = timeit.default_timer()  # measure running time
        working_alg = check_alg_for_root_comp(comp, words_with_max_suffix, comp_pairs)
        if working_alg:
            break

print("Runtime: {:.2f}s".format(timeit.default_timer() - start))

if working_alg:
    print("Algorithm probably succeded")
    # Verify (fill in correct r-values in tree on the way in order to pretty print it)
    result_map = {}
    for word, r in words_with_max_suffix:
        result = MY_UTIL.compute_path_for_word(working_alg, word)
        working_alg[result[-1]].obj = r

        stringed_result = str(result)
        stringed_path = ""
        for node_id in result:
            stringed_path += str(node_id)
            if node_id != result[-1]:
                stringed_path += " [{}]".format(working_alg[node_id].obj)
                stringed_path += " -> "
        if stringed_result in result_map and result_map[stringed_result][1] != r:
            # Found witness path
            print("Not verified!")
            break

        elif word == words_with_max_suffix[-1][0]:
            print("Verified")
            print("Algorithm SUCCEEDED")

            filled_leafs = 0
            for i, node in enumerate(working_alg):
                if MY_UTIL.is_leaf(i) and node.obj != "":
                    filled_leafs += 1
            print("Filled leafs: {}/{}".format(filled_leafs, 3 ** M))
            print("Tree Structure: ")
            for pre, fill, node in RenderTree(working_alg[0]):
                print("%s%s" % (pre, node.obj))
            ts = str(datetime.datetime.now().timestamp() * 1000)
            DotExporter(working_alg[0], nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_picture(
                "{}/{}.png".format(MY_UTIL.base_dir, ts))
            DotExporter(working_alg[0], nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_dotfile(
                "{}/{}.txt".format(MY_UTIL.base_dir, ts))

        result_map[stringed_result] = (word, r)
else:
    print("No possible algorithm exists for finding the max. suffix with N={}, M={}".format(N, M))
