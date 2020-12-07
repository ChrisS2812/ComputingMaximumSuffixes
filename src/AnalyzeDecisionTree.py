import itertools
import json
import os
from pathlib import Path

from tabulate import tabulate

from Util import Util

n = 8
m = 8
UTIL = Util(n, m)

tree = UTIL.load_working_tree([0, 3])

nr_comparisons_count = {}
total_count = 0
difficult_paths = []
r_difficult = []

difficult_words = []
difficult_words_file = os.path.join('Fuzzy', '{}_difficult_words.json'.format(n))

if os.path.exists(difficult_words_file):
    with open(difficult_words_file, 'r') as f:
        difficult_words = json.load(f)
difficult_words_string = [''.join(map(str, w)) for w in difficult_words]

all_words = itertools.product(range(n), repeat=n)
already_seen_comps = {}

base_dir = os.path.join('DecisionTreeAnalysis', '{}_{}'.format(n, m))
Path(base_dir).mkdir(parents=True, exist_ok=True)

txt_filename = "{}.txt".format(n)
txt_filepath = os.path.join(base_dir, txt_filename)

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

        current_node = tree.root
        current_path = []
        count = 0
        while isinstance(current_node.obj, list):
            count += 1
            current_path.append(current_node.obj)
            i1, i2 = current_node.obj
            if word[i1] < word[i2]:
                current_node = current_node.children[0]
            elif word[i1] == word[i2]:
                current_node = current_node.children[1]
            else:
                current_node = current_node.children[2]

        if count not in nr_comparisons_count:
            nr_comparisons_count[count] = 1
        else:
            nr_comparisons_count[count] += 1
        total_count += 1

        if ''.join(map(str, word)) in difficult_words_string:
            difficult_paths.append(current_path)
            r_difficult.append(Util.max_suffix_duval(word))

occ_nr_comparisons = list(nr_comparisons_count.keys())
occ_nr_comparisons.sort()

result_list = []
for comp_val in occ_nr_comparisons:
    result_list.append([comp_val, nr_comparisons_count[comp_val], nr_comparisons_count[comp_val] / total_count * 100])

with open(txt_filepath, 'w') as f:
    print(tabulate(result_list, headers=['#Comparisons', '#Words', 'Percentage'], tablefmt='orgtbl'), file=f)
    print("\nDifficult words:", file=f)
    for i, w in enumerate(difficult_words_string):
        print("{} {} [r={}]".format(w, difficult_paths[i], r_difficult[i]), file=f)
