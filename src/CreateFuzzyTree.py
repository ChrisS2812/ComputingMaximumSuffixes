import itertools
import json
import os
from pathlib import Path

from anytree import Node, LevelOrderIter
from anytree.exporter import DotExporter, JsonExporter
from tabulate import tabulate

from Util import Util

n = 8
MY_UTIL = Util(n, -1)

nr_comparisons_count = {}
difficult_words = []
difficult_paths = []

all_words = itertools.product(range(n), repeat=n)
already_seen_comps = {}

decision_tree = [Node(0, obj=(0, 1))]
max_height = int((4 * n / 3) - 5 / 3)

base_dir = "Fuzzy"
Path(base_dir).mkdir(parents=True, exist_ok=True)
pic_filename = "{}.png".format(n)
txt_filename = "{}.txt".format(n)
dot_filename = "{}.dot".format(n)
json_filename = '{}.json'.format(n)
difficult_words_filename = '{}_difficult_words.json'.format(n)
pic_filepath = os.path.join(base_dir, pic_filename)
dot_filepath = os.path.join(base_dir, dot_filename)
txt_filepath = os.path.join(base_dir, txt_filename)
json_filepath = os.path.join(base_dir, json_filename)
difficult_words_filepath = os.path.join(base_dir, difficult_words_filename)

start_index = 1
for depth in range(1, max_height + 1):
    # create next depth
    for i in range(0, 3 ** depth):
        parent = decision_tree[(start_index + i - 1) // 3]
        decision_tree.append(Node(start_index + i, obj="", parent=parent))
    start_index += 3 ** depth

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

        current_path = []
        current_index = 0
        count = 0

        r = 0
        s = 2
        m = 2
        f = 1
        d = 0
        i = 0
        M = {2: 2}

        while s < n:
            count += 1
            decision_tree[current_index].obj = (s - m, s)
            current_path.append(decision_tree[current_index].obj)

            if word[s] < word[s - m]:
                current_index = current_index * 3 + 3
                s = s + 1
                m = s - r
                M[m] = m
            elif word[s] == word[s - m]:
                current_index = current_index * 3 + 2
                s = s + 1
                M[s - r] = m
            else:
                current_index = current_index * 3 + 1
                d = (s - r) % m
                if d >= f:
                    r = s - d
                    if d > 1:
                        m = M[d]
                    else:
                        m = 2
                        M[2] = 2
                        s = r + 2
                        f = 1
                else:
                    m = m - 1
                    r = s - m
                    f = 0
                    for i in range(3, m + 1):
                        if M[i + 1] < i:
                            M[i] = M[i + 1]
                        else:
                            M[i] = i
        if f > 0 and r < (n - 1):
            count += 1
            decision_tree[current_index].obj = (r, r + 1)
            current_path.append(decision_tree[current_index].obj)
            if word[r] < word[r + 1]:
                r = r + 1
                decision_tree[current_index * 3 + 1].obj = r
            else:
                decision_tree[current_index * 3 + 2].obj = r
                decision_tree[current_index * 3 + 3].obj = r
        else:
            decision_tree[current_index].obj = r

        if count not in nr_comparisons_count:
            nr_comparisons_count[count] = 1
        else:
            nr_comparisons_count[count] += 1
        if (n == 7 and count == n) or (n > 7 and count == n + 1):
            difficult_words.append(word)
            difficult_paths.append(current_path)


def get_edge_label(_, child):
    if child.name % 3 == 1:
        return 'label="<"'
    elif child.name % 3 == 2:
        return 'label="="'
    else:
        return 'label=">"'


Util.clean_up_final_tree(decision_tree[0])

with open(json_filepath, 'w') as f:
    JsonExporter(indent=2).write(decision_tree[0], f)

if n < 7:
    Util.clean_up_final_tree(decision_tree[0])

    #make indices start at 1 for images
    for node in list(LevelOrderIter(decision_tree[0])):
        if isinstance(node.obj, list) or isinstance(node.obj, tuple):
            node.obj = (node.obj[0]+1, node.obj[1]+1)

        elif isinstance(node.obj, int):
            node.obj += 1

    DotExporter(decision_tree[0],
                nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj),
                edgeattrfunc=get_edge_label).to_picture(pic_filepath)

DotExporter(decision_tree[0],
            nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj),
            edgeattrfunc=get_edge_label).to_dotfile(dot_filepath)

occ_nr_comparisons = list(nr_comparisons_count.keys())
occ_nr_comparisons.sort()

result_list = []
for comp_val in occ_nr_comparisons:
    result_list.append([comp_val, nr_comparisons_count[comp_val], nr_comparisons_count[comp_val] / len(already_seen_comps) * 100])

with open(txt_filepath, 'w') as f:
    print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'), file=f)
    print("\nDifficult words:", file=f)
    for i, w in enumerate(difficult_words):
        print("{} {} [r={}]".format(w, difficult_paths[i], Util.max_suffix_duval(w)), file=f)

with open(difficult_words_filepath, 'w') as f:
    json.dump(difficult_words, f)
