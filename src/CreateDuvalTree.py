import itertools
import os
from pathlib import Path

from anytree import Node, LevelOrderIter
from anytree.exporter import DotExporter
from tabulate import tabulate

from Util import Util

n = 4
MY_UTIL = Util(n, -1)

nr_comparisons_count = {}
nr_known_deps_count = {}
difficult_words = []

all_words = itertools.product(range(n), repeat=n)
nr_words = n ** n

decision_tree = [Node(0, obj=(0, 1))]
max_height = int((3 * n / 2) - 2)

base_dir = "Duval"
Path(base_dir).mkdir(parents=True, exist_ok=True)
pic_filename = "{}.png".format(n)
txt_filename = "{}.txt".format(n)
pic_filepath = os.path.join(base_dir, pic_filename)
txt_filepath = os.path.join(base_dir, txt_filename)

start_index = 1
for depth in range(1, max_height + 1):
    # create next depth
    for i in range(0, 3 ** depth):
        parent = decision_tree[(start_index + i - 1) // 3]
        decision_tree.append(Node(start_index + i, obj="", parent=parent))
    start_index += 3 ** depth

for i, word in enumerate(all_words):
    known_deps = []
    if i % 100000 == 0:
        print("{} %".format(i / nr_words * 100))
    current_index = 0
    count = 0
    r = 0
    s = 1
    m = 1
    M = {1: 1}
    while s < n:
        count += 1
        current_comp = [s - m, s]
        decision_tree[current_index].obj = current_comp

        if word[s] < word[s - m]:
            known_deps.append((current_comp, '<'))
            known_deps.extend(MY_UTIL.compute_transitive_dependencies(known_deps, (current_comp, '<')))
            current_index = current_index * 3 + 3
            s = s + 1
            m = s - r
            M[m] = m
        elif word[s] == word[s - m]:
            known_deps.append((current_comp, '='))
            known_deps.extend(MY_UTIL.compute_transitive_dependencies(known_deps, (current_comp, '=')))
            current_index = current_index * 3 + 2
            s = s + 1
            M[s - r] = m
        else:
            known_deps.append((current_comp, '>'))
            known_deps.extend(MY_UTIL.compute_transitive_dependencies(known_deps, (current_comp, '>')))
            current_index = current_index * 3 + 1
            d = (s - r) % m
            if d > 0:
                r = s - d
                m = M.get(d)
            else:
                r = s
                s += 1
                m = 1

    decision_tree[current_index].obj = r
    cleaned_known_deps1 = set(map(lambda x: (tuple(x[0]), x[1]), known_deps))
    cleaned_known_deps2 = filter(lambda x: x[0][0] != x[0][1], cleaned_known_deps1)
    nr_known_deps = len(set(cleaned_known_deps2))

    if nr_known_deps not in nr_known_deps_count:
        nr_known_deps_count[nr_known_deps] = 1
    else:
        nr_known_deps_count[nr_known_deps] += 1

    if count not in nr_comparisons_count:
        nr_comparisons_count[count] = 1
    else:
        nr_comparisons_count[count] += 1

    if (n in [4, 5] and count == n) or (n < 8 and count == n + 1) or (n == 8 and count == 10):
        difficult_words.append(word)


def get_edge_label(_, child):
    if child.name % 3 == 1:
        return 'label="<"'
    elif child.name % 3 == 2:
        return 'label="="'
    else:
        return 'label=">"'


if n < 7:
    Util.clean_up_final_tree(decision_tree[0])

    #make indices start at 1 for images
    for node in list(LevelOrderIter(decision_tree[0])):
        if isinstance(node.obj, list):
            node.obj = [node.obj[0]+1, node.obj[1]+1]

        elif isinstance(node.obj, int):
            node.obj += 1

    DotExporter(decision_tree[0],
                nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj),
                edgeattrfunc=get_edge_label).to_picture(pic_filepath)

occ_nr_comparisons = list(nr_comparisons_count.keys())
occ_nr_comparisons.sort()

nr_known_deps_list = list(nr_known_deps_count.keys())
nr_known_deps_list.sort()


result_list = []
for comp_val in occ_nr_comparisons:
    result_list.append([comp_val, nr_comparisons_count[comp_val], nr_comparisons_count[comp_val] / nr_words * 100])

nr_known_comps_list = []
for nr_val in nr_known_deps_list:
    nr_known_comps_list.append([nr_val, nr_known_deps_count[nr_val], nr_known_deps_count[nr_val] / nr_words * 100])

difficult_words_readable = list(map(lambda x: ''.join(map(str, x)), difficult_words))

print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'))
print(tabulate(nr_known_comps_list, headers=['#Known Comps', '#Words', 'Percentage'], tablefmt='orgtbl'))
print("\nDifficult words:")
for w in difficult_words_readable:
    print("{} [r={}]".format(w, Util.max_suffix_duval(w)))

with open(txt_filepath, 'w') as f:
    print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'), file=f)
    print(tabulate(nr_known_comps_list, headers=['#Known Comps.', '#Words', 'Percentage'], tablefmt='orgtbl'), file=f)
    for w in difficult_words_readable:
        print("{} [r={}]".format(w, Util.max_suffix_duval(w)), file=f)
