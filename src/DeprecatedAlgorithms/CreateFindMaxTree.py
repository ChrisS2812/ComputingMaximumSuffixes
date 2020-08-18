import itertools
import os
from pathlib import Path

from anytree import Node
from anytree.exporter import DotExporter
from tabulate import tabulate
import copy
from src.Util import Util

N = 9
MY_UTIL = Util(N, -1)

nr_comparisons_count = {}
difficult_words = []
    
all_words = itertools.product(range(N), repeat=N)
nr_words = N ** N

decision_tree = [Node(0, obj=(0, 1))]
max_height = 11

base_dir = "FindMax"
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
    leading_max_values_of_maximum = 1
    leading_max_values_current = 0
    max_is_expanding = True
    max_indices = [0]

    # First n-1 comparisons: find maxima
    for i in range(1, len(word)):
        count += 1
        current_comp = (r, i)
        decision_tree[current_index].obj = current_comp

        if word[r] > word[i]:
            current_index = current_index * 3 + 3
            max_is_expanding = False
            leading_max_values_current = 0
        elif word[r] < word[i]:
            current_index = current_index * 3 + 1
            r = i
            max_indices = [r]
            leading_max_values_current = 1
            leading_max_values_of_maximum = 1
            max_is_expanding = True
        else:
            current_index = current_index * 3 + 2
            if max_is_expanding:
                leading_max_values_of_maximum += 1
            else:
                leading_max_values_current += 1
            if leading_max_values_current == leading_max_values_of_maximum:
                max_indices.append(i - leading_max_values_current + 1)

            elif leading_max_values_current > leading_max_values_of_maximum:
                r = i - leading_max_values_current + 1
                max_indices = [r]
                leading_max_values_of_maximum = leading_max_values_current
                max_is_expanding = True

    # last comparisons
    max_suffix_candidates = copy.deepcopy(max_indices)
    while len(max_suffix_candidates) > 1:
        i1 = max_suffix_candidates[0]
        i2 = max_suffix_candidates[1]
        while True:
            if i1 + leading_max_values_of_maximum in max_indices:
                max_suffix_candidates.remove(max_suffix_candidates[1])
                break
            if len(max_indices) > 2 and i2 + leading_max_values_of_maximum in max_indices:
                max_suffix_candidates.remove(max_suffix_candidates[0])
                break
            if i2 + leading_max_values_of_maximum == len(word):
                max_suffix_candidates.remove(max_suffix_candidates[1])
                break
            else:
                count += 1
                current_comp = (i1 + leading_max_values_of_maximum, i2 + leading_max_values_of_maximum)
                decision_tree[current_index].obj = current_comp
            if word[i1 + leading_max_values_of_maximum] < word[i2 + leading_max_values_of_maximum]:
                current_index = current_index * 3 + 1
                max_suffix_candidates.remove(max_suffix_candidates[0])
                break
            elif word[i1 + leading_max_values_of_maximum] > word[i2 + leading_max_values_of_maximum]:
                current_index = current_index * 3 + 3
                max_suffix_candidates.remove(max_suffix_candidates[1])
                break
            else:
                current_index = current_index * 3 + 2
                i1 += 1
                i2 += 1

    if count not in nr_comparisons_count:
        nr_comparisons_count[count] = 1
    else:
        nr_comparisons_count[count] += 1
    if N == 9 and count == 12:
        difficult_words.append(word)

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
