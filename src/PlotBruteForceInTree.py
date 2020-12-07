#!/usr/bin/env python
# coding: utf-8

import copy
import os
# This tries to find an algorithm that finds the longest suffix of any given word with length N while using only M
# comparisons
from time import gmtime, strftime

import networkx as nx
from anytree import Node, PreOrderIter
from graphviz import Digraph
from python_algorithms.basic.union_find import UF

from Util import Util

n = 4
m = 3
DEBUG = True
MY_UTIL = Util(n, m)
ALL_COMPS = MY_UTIL.comp_pairs
NR_COMPS = len(ALL_COMPS)

USE_OPTIM2 = True
USE_ALL_OPTIM = True

ROOT_COMP = [0,2]

X_POSITIONS_M2 = [0, -1, 0, 1]
X_POSITIONS_M3 = [0, -3.5, 0, 3.5, -4.5, -3.5, -2.5, -1, 0, 1, 2.5, 3.5, 4.5]

OUTPUT_DIR = 'StratTree/n{}m{}/NonOptim/c{}'.format(n, m, ROOT_COMP)
if USE_ALL_OPTIM:
    OUTPUT_DIR = 'StratTree/n{}m{}/FullOptim/c{}'.format(n, m, ROOT_COMP)
elif USE_OPTIM2:
    OUTPUT_DIR = 'StratTree/n{}m{}/Optim2/c{}'.format(n, m, ROOT_COMP)

COLORS = ['red', 'yellow', 'green', 'blue', 'indigo']
SIGNATURE = '1'
TREE = Digraph(format='svg', strict=True, engine='neato')

# define how many comparisons are allowed that do not extend the underlying dependency graph
max_m = int((4 * n - 5) / 3)
max_non_endogeneous = max_m - n + 1


def delete_from_tree(sign):
    newTreeBody = list(filter(lambda entry: not str.startswith(entry, '\t{}'.format(sign)), TREE.body))
    TREE.body = newTreeBody


def build_filename(current_node):
    filename = ''
    for node in PreOrderIter(current_node.root):
        if node == current_node:
            filename = filename + str(node.obj[0]) + str(node.obj[1])
            break
        if not node.is_leaf:
            filename = filename + str(node.obj[0]) + str(node.obj[1])
    return filename


def create_strategy_tree():
    output_file = '{}/{}'.format(OUTPUT_DIR, 'strategy_tree')

    file_map = {}
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".svg") and not file.startswith('strategy_tree'):
            filename_len = len(file)
            if filename_len in file_map:
                file_map[filename_len].append(os.path.splitext(file)[0])
            else:
                file_map[filename_len] = [os.path.splitext(file)[0]]
    for key in file_map:
        file_map[key].sort()

    keys_sorted = list(file_map.keys())
    keys_sorted.sort()

    # Create root of strategy tree
    strategy_tree = Digraph(format='svg', strict=True)
    strategy_tree.node(file_map[keys_sorted[0]][0], '', image="{}.{}".format(file_map[keys_sorted[0]][0], 'svg'),
                       shape='box', penwidth='3.0')

    for prev_index, key in enumerate(keys_sorted[1:]):
        for file in file_map[key]:
            strategy_tree.node(file, '', image="{}.{}".format(file, 'svg'), shape='box', penwidth='3.0')
            max_nr_matches = -1
            parent = None
            for parent_candidate in file_map[keys_sorted[prev_index]]:
                curr_nr_matches = 0
                for i, char in enumerate(parent_candidate):
                    if char == file[i]:
                        curr_nr_matches += 1
                    else:
                        break
                if curr_nr_matches > max_nr_matches:
                    max_nr_matches = curr_nr_matches
                    parent = parent_candidate
            strategy_tree.edge(parent, file)
    strategy_tree.render(output_file)


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
    global TREE

    root_node = generate_algorithm(root_comp)

    TREE.node(SIGNATURE, '', style='filled', fillcolor='{};0.5:{}'.format(COLORS[root_comp[0]], COLORS[root_comp[1]]),
              pos="{},{}!".format(0, m - 1))
    filename = build_filename(root_node)
    TREE.render('{}/{}'.format(OUTPUT_DIR, filename))

    if DEBUG:
        print("({}) Starting checking of algorithms with root value {}".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                                                                               root_comp))

    bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(root_comp, words)

    # union-find datastructure that is used to keep track if the underlying ordering graph is yet weakly connected
    G_smaller = None
    G_equal = None
    G_bigger = None
    cc = None
    if USE_ALL_OPTIM:
        cc = UF(n)
        cc.union(root_comp[0], root_comp[1])

        # graph that keeps track of transitive dependencies
        G = nx.DiGraph()
        G.add_nodes_from(range(n))

        G_smaller = G.copy()
        G_equal = G.copy()
        G_bigger = G.copy()

        G_smaller.add_edge(root_comp[0], root_comp[1])
        G_equal.add_edge(root_comp[0], root_comp[1])
        G_equal.add_edge(root_comp[1], root_comp[0])
        G_bigger.add_edge(root_comp[1], root_comp[0])

    # If, for a word w=a_1 a_2 ... a_n, we already know that the max_suffix is in the subword a_i ... a_n and we
    # conduct a comparison between the a_i and a_j which yields  a_i < a_j we can subsequently only
    # investigate the subword a_{i+1} a_{i+2} ... a_n
    comps_new_smaller = comps
    comps_new_equal = comps
    comps_new_bigger = comps
    first_rel_char_smaller = None
    if USE_OPTIM2 or USE_ALL_OPTIM:
        comps_new_smaller = [c for c in comps if c != root_comp]
        comps_new_equal = [c for c in comps if c != root_comp]
        comps_new_bigger = [c for c in comps if c != root_comp]
        if root_comp[0] == 0:
            comps_new_smaller = [c for c in comps if c[0] != 0] + [c for c in comps if c[0] == 0]
            first_rel_char_smaller = 1
        else:
            first_rel_char_smaller = 0

    if (check_alg(root_node.children[0], smaller_list, comps_new_smaller, cc, G_smaller, first_rel_char_smaller)
            and check_alg(root_node.children[1], equal_list, comps_new_equal, cc, G_equal, 0)
            and check_alg(root_node.children[2], bigger_list, comps_new_bigger, cc, G_bigger, 0)):
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return root_node
    else:
        MY_UTIL.save_current_graph(root_node.root, is_final=True)
        return


# Recursively checks all possible decision trees with a given root-value in a Divide and Conquer approach.
# Returns 'True' if a correct decision tree was found.
def check_alg(current_node, words, comps, connected_components, dep_graph, first_rel_char):
    global TREE, SIGNATURE

    if len(SIGNATURE) == current_node.depth:
        # came from one depth above -> start new enumeration of this depth
        SIGNATURE = SIGNATURE[:current_node.depth] + "1"
    else:
        # came from depth below -> increment previous enumeration
        SIGNATURE = SIGNATURE[:current_node.depth] + str(int(SIGNATURE[current_node.depth]) + 1)

    TREE.edge(SIGNATURE[:-1], SIGNATURE)

    # If only one word is left from previous comparisons we can immediately decide for this words r-value
    if (USE_OPTIM2 or USE_ALL_OPTIM) and not comps or len([l for l in words if len(l) > 0]) <= 1:
        return True

    if current_node.depth < m - 1:
        # Divide - here we want to check all possible values for the node (that have not yet been checked)
        for c_new in comps:
            current_node.obj = c_new

            print("Checking {} for node {}".format(c_new, current_node))

            if len(SIGNATURE) > current_node.depth + 1:
                delete_from_tree(SIGNATURE[:current_node.depth + 1])
                SIGNATURE = SIGNATURE[:current_node.depth + 1]

            if m == 3:
                TREE.node(SIGNATURE, '', style='filled',
                          fillcolor='{};0.5:{}'.format(COLORS[c_new[0]], COLORS[c_new[1]]),
                          pos="{},{}!".format(X_POSITIONS_M3[int(current_node.name)], m - 1 - current_node.depth))
            elif m == 2:
                TREE.node(SIGNATURE, '', style='filled',
                          fillcolor='{};0.5:{}'.format(COLORS[c_new[0]], COLORS[c_new[1]]),
                          pos="{},{}!".format(X_POSITIONS_M2[int(current_node.name)], m - 1 - current_node.depth))

            filename = build_filename(current_node)
            TREE.render('{}/{}'.format(OUTPUT_DIR, filename))

            bigger_list, equal_list, smaller_list = MY_UTIL.divide_words(current_node.obj, words)

            # prepare list of remaining comparions for each child
            comps_smaller = comps
            comps_equal = comps
            comps_bigger = comps

            first_rel_char_smaller = first_rel_char
            first_rel_char_equal = first_rel_char
            first_rel_char_bigger = first_rel_char
            if USE_OPTIM2 or USE_ALL_OPTIM:
                comps_smaller = [c for c in comps if c != c_new]
                comps_equal = [c for c in comps if c != c_new]
                comps_bigger = [c for c in comps if c != c_new]

                if c_new[0] == first_rel_char:
                    comps_smaller = [c for c in comps_smaller if c[0] != first_rel_char] + [c for c in comps_smaller if c[0] == first_rel_char]
                    first_rel_char_smaller = first_rel_char + 1

            cc1 = None
            cc2 = None
            cc3 = None
            dep_graph_smaller = None
            dep_graph_equal = None
            dep_graph_bigger = None

            if USE_ALL_OPTIM:
                cc1 = copy.deepcopy(connected_components)
                cc2 = copy.deepcopy(connected_components)
                cc3 = copy.deepcopy(connected_components)

                cc1.union(c_new[0], c_new[1])
                cc2.union(c_new[0], c_new[1])
                cc3.union(c_new[0], c_new[1])

                dep_graph_smaller = dep_graph.copy()
                dep_graph_equal = dep_graph.copy()
                dep_graph_bigger = dep_graph.copy()

                dep_graph_smaller.add_edge(c_new[0], c_new[1])
                dep_graph_equal.add_edge(c_new[0], c_new[1])
                dep_graph_equal.add_edge(c_new[1], c_new[0])
                dep_graph_bigger.add_edge(c_new[1], c_new[0])

                # find nodes that are smaller/bigger than the character at c_new[0]
                trans_smaller_bigger = nx.descendants(dep_graph_smaller, c_new[1])
                trans_smaller_bigger.add(c_new[1])

                trans_smaller_smaller = nx.descendants(dep_graph_smaller.reverse(False), c_new[0])
                trans_smaller_smaller.add(c_new[0])

                trans_bigger_bigger = nx.descendants(dep_graph_bigger, c_new[0])
                trans_bigger_bigger.add(c_new[0])

                trans_bigger_smaller = nx.descendants(dep_graph_bigger.reverse(False), c_new[1])
                trans_bigger_smaller.add(c_new[1])

                # remove transitively determined dependencies from further consideration
                for i in trans_smaller_smaller:
                    for j in trans_smaller_bigger:
                        if sorted([i, j]) in comps_smaller:
                            comps_smaller.remove(sorted([i, j]))
                        if sorted([i, j]) in comps_equal:
                            comps_equal.remove(sorted([i, j]))

                for i in trans_bigger_smaller:
                    for j in trans_bigger_bigger:
                        if sorted([i, j]) in comps_bigger:
                            comps_bigger.remove(sorted([i, j]))
                        if sorted([i, j]) in comps_equal:
                            comps_equal.remove(sorted([i, j]))

                while nx.descendants(dep_graph_smaller, first_rel_char_smaller) - nx.descendants(dep_graph_smaller.reverse(True), first_rel_char_smaller):
                    first_rel_char_smaller += 1
                comps_smaller = [c for c in comps_smaller if c[0] >= first_rel_char_smaller] + [c for c in comps_smaller if
                                                                                               c[0] < first_rel_char_smaller]

                while nx.descendants(dep_graph_equal, first_rel_char_equal) - nx.descendants(dep_graph_equal.reverse(True), first_rel_char_equal):
                    first_rel_char_equal += 1
                comps_equal = [c for c in comps_equal if c[0] >= first_rel_char_equal] + [c for c in comps_equal if
                                                                                          c[0] < first_rel_char_equal]

                while nx.descendants(dep_graph_bigger, first_rel_char_bigger) - nx.descendants(dep_graph_bigger.reverse(True), first_rel_char_bigger):
                    first_rel_char_bigger += 1
                comps_bigger = [c for c in comps_bigger if c[0] >= first_rel_char_bigger] + [c for c in comps_bigger if
                                                                                             c[0] < first_rel_char_bigger]

            if (check_alg(current_node.children[0], smaller_list, comps_smaller, cc1,
                      dep_graph_smaller,
                      first_rel_char_smaller) and
                check_alg(current_node.children[1], equal_list, comps_equal,
                          cc2, dep_graph_equal, first_rel_char_equal) and
                check_alg(current_node.children[2], bigger_list, comps_bigger,
                          cc3, dep_graph_bigger, first_rel_char_bigger)):
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

            print("Checking {} for node {}".format(c_new, current_node))

            if m == 3:
                TREE.node(SIGNATURE, '', style='filled',
                          fillcolor='{};0.5:{}'.format(COLORS[c_new[0]], COLORS[c_new[1]]),
                          pos="{},{}!".format(X_POSITIONS_M3[int(current_node.name)], m - 1 - current_node.depth))
            elif m == 2:
                TREE.node(SIGNATURE, '', style='filled',
                          fillcolor='{};0.5:{}'.format(COLORS[c_new[0]], COLORS[c_new[1]]),
                          pos="{},{}!".format(X_POSITIONS_M2[int(current_node.name)], m - 1 - current_node.depth))

            old_obj = current_node.obj
            current_node.obj = c_new
            filename = build_filename(current_node)
            TREE.render('{}/{}'.format(OUTPUT_DIR, filename))
            current_node.obj = old_obj

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
wdtimes = []
words_with_max_suffix = MY_UTIL.generate_all_words()

working_algs = []

working_algs.append(check_alg_for_root_comp(ROOT_COMP, words_with_max_suffix, MY_UTIL.comp_pairs))

for i, root in enumerate(working_algs):
    MY_UTIL.check_valid(root)

create_strategy_tree()
