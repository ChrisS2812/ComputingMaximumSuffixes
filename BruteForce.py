#!/usr/bin/env python
# coding: utf-8

# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
import copy
import datetime
import itertools
import os
import threading
import time
import timeit
from multiprocessing import Pool
from os import listdir
from os.path import isfile, join
from pathlib import Path

from anytree import Node, RenderTree, LevelOrderIter
from anytree.exporter import DotExporter, JsonExporter
from anytree.importer import JsonImporter

N = 5
M = 5
DEBUG = True
ONLY_HIGHEST_DEBUG = True
NR_WORKERS = 1

dir = "N{}M{}".format(N, M)
Path(dir).mkdir(parents=True, exist_ok=True)
checkpoint_dir = os.path.join(dir, 'checkpoint')
Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

# Compute all possible pairs of indices that can be compared
comp_pairs = []
for i in range(N):
    for j in range(i + 1, N):
        comp_pairs.append((i, j))
print(comp_pairs)


# Duval's algorithm for finding the index of maximum suffix
def max_suffix_duval(word):
    r = 0
    s = 1
    m = 1
    n = len(word)
    M = {}
    M[1] = 1
    while s < n:
        if word[s] < word[s - m]:
            s = s + 1
            m = s - r
            M[m] = m
        elif word[s] == word[s - m]:
            s = s + 1
            M[s - r] = m
        else:
            d = (s - r) % m
            if d > 0:
                r = s - d
                m = M[d]
            else:
                r = s
                s += 1
                m = 1
    return r


# Create all possible words for a given N
def generate_all_word_with_max_suffix():
    # List of all words
    all_words = list(itertools.product(range(N), repeat=N))

    # Reduce this to list of relevant words by defining two words as equivalent if all its pairwise comparisons have
    # the same result
    comp_result_2_word = {}
    for w in all_words:
        comparisons = ""
        for i in range(N):
            for j in range(i + 1, N):
                c1 = w[i]
                c2 = w[j]
                if c1 < c2:
                    comparisons += "<"
                elif c1 > c2:
                    comparisons += ">"
                else:
                    comparisons += "="
        if comparisons not in comp_result_2_word:
            comp_result_2_word[comparisons] = w

    rel_words = []

    for entry in comp_result_2_word.values():
        w = ''
        for char in entry:
            w += str(char)
        rel_words.append(w)

    # Create the correct maximum suffix index for each relevant word and save it together with word in tuple
    result = []
    for w in rel_words:
        result.append((w, max_suffix_duval(w)))

    return result


# Helping function that computes the path of of a given word in a given decision tree in the form:
# * (n_1,...,n_m) where n_i represents the id of the i'th node
def compute_path_for_word(alg, word):
    current_index = 0
    path = []
    while current_index < len(alg):
        path.append(current_index)
        if is_leaf(current_index):
            break
        i1, i2 = alg[current_index].obj
        c1 = word[i1]
        c2 = word[i2]
        if c1 < c2:
            current_index = current_index * 3 + 1
        elif c1 == c2:
            current_index = current_index * 3 + 2
        else:
            current_index = current_index * 3 + 3
    return path


# Helping function that computes (all) decision-tree-independent path representation on which a given index lies. A path is a string of the form
# * c_1r_1c_2_r_2...c_M
#
# where c_i represents a comparison and r_i the result of this comparison ("<", "=", or ">")
def compute_path_repr_for_index(alg, index):
    if is_leaf(index):
        return compute_path_repr_for_index(alg, (index - 1) // 3)
    if is_last_comp(index):
        # start at lowest comparison node (the last node is not important for blacklisted paths)
        repr = str(alg[index].obj)
        while index != 0:
            mod = index % 3
            if mod == 0:
                repr = ">" + repr
            elif mod == 1:
                repr = "<" + repr
            else:
                repr = "=" + repr
            index = (index - 1) // 3
            repr = str(alg[index].obj) + repr
        return [repr]
    else:
        result = []
        # Append paths for all children
        result.extend(compute_path_repr_for_index(alg, index * 3 + 1))
        result.extend(compute_path_repr_for_index(alg, index * 3 + 2))
        result.extend(compute_path_repr_for_index(alg, index * 3 + 3))
        return result


# Helping function that decides whether a node at a given index is a leaf or not.
def is_leaf(index):
    if M < 1:
        return True

    last_non_leaf_index = -1
    for i in range(0, M):
        last_non_leaf_index += 3 ** i
    if index <= last_non_leaf_index:
        return False
    else:
        return True


# Helping function that decides whether a node at a given index represents the last comparison
def is_last_comp(index):
    if M < 1:
        return False
    if M == 2:
        if index == 0:
            return True
        else:
            return False

    if is_leaf(index):
        return False

    last_non_last_comp_index = -1
    for i in range(0, M - 1):
        last_non_last_comp_index += 3 ** i

    if index > last_non_last_comp_index:
        return True
    else:
        return False


# Helping function that computes for a list of previously executed comparison and a new (current) comparison whether,
# after carrying out the new comparison, any other comparisons can be deduced transitively
# todo add fitting sign to return
def compute_transitive_dependencies(previous_comps, current_comp):
    result = []
    (cc1, cc2), cr = current_comp
    for (pc1, pc2), pr in previous_comps:
        if cc1 == pc1:
            # (i,j) and (i,k)
            if cr == '=' or pr == '=' or (cr == '<' and pr == '>') or (cr == '>' and pr == '<'):
                result.append(tuple(sorted((cc2, pc2))))
        elif cc2 == pc2:
            # (i,j) and (k,j)
            if cr == '=' or pr == '=' or (cr == '<' and pr == '>') or (cr == '>' and pr == '<'):
                result.append(tuple(sorted((cc1, pc1))))
        elif cc1 == pc2:
            # (i,j) and (k,i):
            if cr == '=' or pr == '=' or (cr == '<' and pr == '<') or (cr == '>' and pr == '>'):
                result.append(tuple(sorted((cc2, pc1))))
        elif cc2 == pc1:
            # (i,j) and (j,k):
            if cr == '=' or pr == '=' or (cr == '<' and pr == '<') or (cr == '>' and pr == '>'):
                result.append(tuple(sorted((cc1, pc2))))
    return result


# Generates a decision tree for M comparisons with given root value that fulfils the following rule(s):
# 1. No path contains the same node value twice
#
# Define a tree structure inside a list, each representing a different height of the tree. Anytree helps us navigating the tree (i.e. finding children, parents etc.)
def generate_algorithm(root_value):
    alg = []
    current_index = 0
    for i in range(M + 1):
        if i == 0:
            # Root Node
            root = Node(current_index, obj=root_value)
            alg.append(root)
            current_index += 1
        elif i == M:
            # Leaf Nodes
            for j in range(3 ** M):
                parent = alg[(current_index - 1) // 3]
                alg.append(Node(current_index, obj="", parent=parent))
                current_index += 1
        else:
            for j in range(3 ** i):
                parent = alg[(current_index - 1) // 3]
                parent_index = current_index
                parent_values = []
                # Collect all values of (grand-)parents of the current node
                while parent_index != 0:
                    parent_index = (parent_index - 1) // 3
                    parent_values.append(alg[parent_index].obj)

                for pair in comp_pairs:
                    if pair not in parent_values:
                        alg.append(Node(current_index, obj=pair, parent=parent))
                        current_index += 1
                        break
    return alg


# Helping function that saves current state of algorithm (i.e. the current tree) to a file from which it can be
# reloaded.
def save_current_graph(root, interval):
    i = 0
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        if i == interval:
            # time for a regular save
            ts = str(datetime.datetime.now().timestamp() * 1000)
            filename = "{}_{}.json".format(root.obj, ts)
            final_path = os.path.join(checkpoint_dir, filename)
            with open(final_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)
            i = 0
        else:
            # Nothing to do here
            time.sleep(1)
            # dirty solution for regularly checking for liveness
            i += 1

    # save a last time
    ts = str(datetime.datetime.now().timestamp() * 1000)
    filename = "{}_{}.json".format(root.obj, ts)
    final_path = os.path.join(checkpoint_dir, filename)
    with open(final_path, 'w') as f:
        JsonExporter(indent=2).write(root, f)


def load_alg_from_checkpoint(root_comp):
    chkpnt_files = [f for f in listdir(checkpoint_dir) if isfile(join(checkpoint_dir, f))
                    and f.startswith(str(root_comp))]

    if not chkpnt_files:
        return -1

    chkpnt_files.sort()
    most_recent_checkpoint = chkpnt_files[-1]

    path_to_most_recent_checkpoint = os.path.join(checkpoint_dir, most_recent_checkpoint)

    with open(path_to_most_recent_checkpoint, 'r') as f:
        root = JsonImporter().read(f)

    alg = [node for node in LevelOrderIter(root)]
    for node in alg:
        node.obj = tuple(node.obj)

    return alg


# TODO: describe
def check_alg_for_root_comp(root_comp, words_with_max_suffix, comps):
    alg = load_alg_from_checkpoint(root_comp)
    if alg == -1:
        alg = generate_algorithm(root_comp)
    if DEBUG:
        print("Starting checking of algorithms with root value {}".format(root_comp))
    result = check_alg(alg, 0, words_with_max_suffix, comps, [])
    return result

# TODO: describe
def check_alg(alg, index, words, comps, prev_comps):
    # Divide and Conquer
    if not is_last_comp(index):
        if index == 0:
            # Compute three subsets of the words and of the tree
            i1, i2 = alg[index].obj
            smaller_list = []
            equal_list = []
            bigger_list = []
            for entry in words:
                word = entry[0]
                if word[i1] < word[i2]:
                    smaller_list.append(entry)
                elif word[i1] == word[i2]:
                    equal_list.append(entry)
                else:
                    bigger_list.append(entry)
            # this is only executed once - use this place to start a thread that regularly saves checkpoints
            save_thread = threading.Thread(target=save_current_graph, args=(alg[0], 1800))
            try:
                save_thread.start()
            except (KeyboardInterrupt, SystemExit):
                # Cleanup on interrupt
                save_thread.do_run = False
                save_thread.join()

            # remove the comparison value at the current node from further consideration
            comps_new_smaller = copy.deepcopy(comps)
            comps_new_equal = copy.deepcopy(comps)
            comps_new_bigger = copy.deepcopy(comps)

            current_comp = alg[index].obj

            comps_new_smaller.remove(current_comp)
            comps_new_equal.remove(current_comp)
            comps_new_bigger.remove(current_comp)
            # Note: We do not want to manipulate the root - different values will be checked in other executions
            if (check_alg(alg, index * 3 + 1, smaller_list, comps_new_smaller, [(current_comp, '<')]) and
                    check_alg(alg, index * 3 + 2, equal_list, comps_new_equal, [(current_comp, '=')]) and
                    check_alg(alg, index * 3 + 3, bigger_list, comps_new_bigger, [(current_comp, '>')])):
                # Cleanup on finishing
                save_thread.do_run = False
                save_thread.join()
                return alg
            else:
                save_thread.do_run = False
                save_thread.join()
                return
        else:
            # not at root - here we want to check all possible values for the node, so we loop over comps
            for c_new in comps:
                if DEBUG and (not ONLY_HIGHEST_DEBUG or index < 4):
                    print("[Increasing] Increasing index {} from {} to {}".format(index, alg[index].obj, c_new))

                alg[index].obj = c_new

                # Compute three subsets of the words and of the tree
                i1, i2 = alg[index].obj
                smaller_list = []
                equal_list = []
                bigger_list = []
                for entry in words:
                    word = entry[0]
                    if word[i1] < word[i2]:
                        smaller_list.append(entry)
                    elif word[i1] == word[i2]:
                        equal_list.append(entry)
                    else:
                        bigger_list.append(entry)

                # Compute all comparisons that can be transitively deduced for each possible outcome
                transitive_smaller = compute_transitive_dependencies(prev_comps, (c_new, '<'))
                transitive_equal = compute_transitive_dependencies(prev_comps, (c_new, '='))
                transitive_bigger = compute_transitive_dependencies(prev_comps, (c_new, '>'))

                # remove current comparison and transitively clear comparisons
                # from further consideration

                comps_smaller_new = copy.deepcopy(comps)
                comps_smaller_new.remove(c_new)
                for comp in [t for t in transitive_smaller if t in comps]:
                    comps_smaller_new.remove(comp)

                comps_equal_new = copy.deepcopy(comps)
                comps_equal_new.remove(c_new)
                for comp in [t for t in transitive_equal if t in comps]:
                    comps_equal_new.remove(comp)

                comps_bigger_new = copy.deepcopy(comps)
                comps_bigger_new.remove(c_new)
                for comp in [t for t in transitive_bigger if t in comps]:
                    comps_bigger_new.remove(comp)

                # todo update prev_comps
                if (check_alg(alg, index * 3 + 1, smaller_list, comps_smaller_new, prev_comps) and
                        check_alg(alg, index * 3 + 2, equal_list, comps_equal_new, prev_comps) and
                        check_alg(alg, index * 3 + 3, bigger_list, comps_bigger_new, prev_comps)):
                    return True
            return False

    else:
        for c_new in comps:
            result_map = {}
            alg[index].obj = c_new

            for word, r in words:
                result = compute_path_for_word(alg, word)

                stringed_result = str(result)
                stringed_path = ""
                for node_id in result:
                    stringed_path += str(node_id)
                    if node_id != result[-1]:
                        stringed_path += " [{}]".format(alg[node_id].obj)
                        stringed_path += " -> "
                if stringed_result in result_map and result_map[stringed_result][1] != r:
                    break

                elif word == words[-1][0]:
                    return True

                else:
                    result_map[stringed_result] = (word, r)

        return False


# Helping function that stop the workers early when a solution was found
working_alg = []


def check_result(return_alg):
    global working_alg
    if not working_alg and return_alg is not None:
        working_alg = return_alg
        workers.terminate()


words_with_max_suffix = generate_all_word_with_max_suffix()
print("Need to find Algorithm for {} interesting words".format(len(words_with_max_suffix)))

start = timeit.default_timer()  # measure running time

if NR_WORKERS > 1:
    # worker pool - each worker is responsible for a single root value
    workers = Pool(processes=NR_WORKERS)
    try:
        results = []
        for comp in comp_pairs:
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
        working_alg = check_alg_for_root_comp(comp, words_with_max_suffix, comp_pairs)
        if working_alg:
            break

print("Runtime: {:.2f}s".format(timeit.default_timer() - start))

if working_alg:
    print("Algorithm probably succeded")
    # Verify (fill in correct r-values in tree on the way in order to pretty print it)
    result_map = {}
    for word, r in words_with_max_suffix:
        result = compute_path_for_word(working_alg, word)
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
                if is_leaf(i) and node.obj != "":
                    filled_leafs += 1
            print("Filled leafs: {}/{}".format(filled_leafs, 3 ** M))
            print("Tree Structure: ")
            for pre, fill, node in RenderTree(working_alg[0]):
                print("%s%s" % (pre, node.obj))
            ts = str(datetime.datetime.now().timestamp() * 1000)
            DotExporter(working_alg[0], nodeattrfunc=lambda node: 'label="{}"'.format(node.obj)).to_picture(
                "{}/{}.png".format(dir, ts))
            DotExporter(working_alg[0], nodeattrfunc=lambda node: 'label="{}"'.format(node.obj)).to_dotfile(
                "{}/{}.txt".format(dir, ts))

        result_map[stringed_result] = (word, r)
else:
    print("No possible algorithm exists for finding the max. suffix with N={}, M={}".format(N, M))
