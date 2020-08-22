import itertools
import os
from pathlib import Path

from anytree import Node
from anytree.exporter import DotExporter
from tabulate import tabulate

from src.Util import Util

n = 9
MY_UTIL = Util(n, -1)

nr_comparisons_count = {}
difficult_words = []

all_words = itertools.product(range(n), repeat=n)
nr_words = n ** n

decision_tree = [Node(0, obj=(0, 1))]
max_height = int((4 * n / 3) - 5 / 3)

base_dir = "Fuzzy"
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
    if i % 100000 == 0:
        print("{} %".format(i / nr_words * 100))
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
        current_comp = (s - m, s)
        decision_tree[current_index].obj = current_comp

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
    if (n < 8 and count == n) or (n == 8 and count == n + 1):
        difficult_words.append(word)


def get_edge_label(_, child):
    if child.name % 3 == 1:
        return 'label="<"'
    elif child.name % 3 == 2:
        return 'label="="'
    else:
        return 'label=">"'


if n < 7:
    DotExporter(decision_tree[0],
                nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj),
                edgeattrfunc=get_edge_label).to_picture(pic_filepath)

occ_nr_comparisons = list(nr_comparisons_count.keys())
occ_nr_comparisons.sort()

result_list = []
for comp_val in occ_nr_comparisons:
    result_list.append([comp_val, nr_comparisons_count[comp_val], nr_comparisons_count[comp_val] / nr_words * 100])

difficult_words_readable = list(map(lambda x: ''.join(map(str, x)), difficult_words))
print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'))
print("\nDifficult words:")
for w in difficult_words_readable:
    print("{} [r={}]".format(w, MY_UTIL.max_suffix_duval(w)))

with open(txt_filepath, 'w') as f:
    print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'), file=f)
    print("\nDifficult words:", file=f)
    for w in difficult_words_readable:
        print("{} [r={}]".format(w, MY_UTIL.max_suffix_duval(w)), file=f)
