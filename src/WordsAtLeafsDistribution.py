from statistics import median

from anytree import Node, LevelOrderIter
import matplotlib.pyplot as plt
from Util import Util

n = 8
m = 8

MY_UTIL = Util(n, m)

root = MY_UTIL.load_working_tree([0,3])

for node in LevelOrderIter(root):
    new_children = []
    for i, child in enumerate(node.children):
        if child.is_leaf:
            new_children.append(Node(child.name, obj=child.obj, parent=node, nr_words=0))
        else:
            new_children.append(child)
    node.children = tuple(new_children)

for words in MY_UTIL.generate_all_words():
    for w in words:
        current_node = root
        while not current_node.is_leaf:
            i1, i2 = current_node.obj
            c1 = w[i1]
            c2 = w[i2]
            if c1 < c2:
                current_node = current_node.children[0]
            elif c1 == c2:
                current_node = current_node.children[1]
            else:
                current_node = current_node.children[2]

        current_node.nr_words += 1

words_numbers = []
for l in root.leaves:
    words_numbers.append(l.nr_words)

print("Mean: {}".format(sum(words_numbers) / len(words_numbers)))
print("Median: {}".format(median(words_numbers)))

plt.hist(words_numbers, density=False, bins=100)
plt.show()