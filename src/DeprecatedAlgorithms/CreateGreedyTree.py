import itertools
import os
from pathlib import Path

from anytree import Node
from anytree.exporter import DotExporter
from tabulate import tabulate

from src.Util import Util

N = 6
MY_UTIL = Util(N, -1)

nr_comparisons_count = {}
difficult_words = []
    
all_words = itertools.product(range(N), repeat=N)
nr_words = N ** N

decision_tree = [Node(0, obj=(0, 1))]
max_height = 8

base_dir = "Greedy"
Path(base_dir).mkdir(parents=True, exist_ok=True)
pic_filename = "{}.png".format(N)
txt_filename = "{}.txt".format(N)
pic_filepath = os.path.join(base_dir, pic_filename)
txt_filepath = os.path.join(base_dir, txt_filename)

start_index = 2
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
    i = 1
    leading_max_values_of_maximum = 1
    leading_max_values_current = 1
    max_is_expanding = True

    while i < len(word):
        count += 1
        current_comp = (r, i)
        decision_tree[current_index].obj = current_comp

        if word[r] < word[i]:
            current_index = current_index * 3 + 1
            r = i
            i = r+1
            leading_max_values_of_maximum = 1
            leading_max_values_current = 0
            max_is_expanding = True
        elif word[r] > word[i]:
            current_index = current_index * 3 + 3
            i += 1
            leading_max_values_current = 0
            max_is_expanding = False

        else:
            current_index = current_index * 3 + 2
            leading_max_values_current += 1
            i += 1

            if max_is_expanding:
                leading_max_values_of_maximum += 1
                continue

            if leading_max_values_current == leading_max_values_of_maximum:
                j = r + leading_max_values_of_maximum - 1
                k = i - 1

                while True:
                    j += 1
                    k += 1
                    if k >= len(word):
                        i = len(word)
                        break

                    current_comp = (j, r)
                    decision_tree[current_index].obj = current_comp
                    count += 1

                    if word[j] > word[k]:
                        current_index = current_index * 3 + 3
                        break
                    elif word[j] < word[k]:
                        current_index = current_index * 3 + 1
                        r = i - leading_max_values_current
                        break
                    else:
                        current_index = current_index * 3 + 2

            if leading_max_values_current > leading_max_values_of_maximum:
                r = i - leading_max_values_current
                leading_max_values_of_maximum = leading_max_values_current
                leading_max_values_current = 0
                i = r + leading_max_values_of_maximum
                max_is_expanding = True
    if count == 9:
        print(word)
    if count not in nr_comparisons_count:
        nr_comparisons_count[count] = 1
    else:
        nr_comparisons_count[count] += 1

def get_edge_label(_, child):
    if child.name % 3 == 1:
        return 'label="<"'
    elif child.name % 3 == 2:
        return 'label="="'
    else:
        return 'label=">"'


# if N < 7:
#     DotExporter(decision_tree[0],
#                 nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj),
#                 edgeattrfunc=get_edge_label).to_picture(pic_filepath)

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
