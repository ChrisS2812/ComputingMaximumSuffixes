import json

from anytree import Node

from Util import Util

UTIL = Util(8, 8)

tree = UTIL.load_working_tree([0,2])
fuzzy_tree = UTIL.load_fuzzy_tree(8)

with open("Fuzzy/8_difficult_words.json", "r") as f:
    difficult_words = json.load(f)

for word in difficult_words:
    print("=========================================")
    print("Word: {}".format(word))

    current_node = tree.root
    current_path = []
    count = 0
    while isinstance(current_node.obj, list):
        if len(current_node.children) == 0:
            Node(current_node.name * 3 + 1, obj="", parent=current_node)
            Node(current_node.name * 3 + 2, obj="", parent=current_node)
            Node(current_node.name * 3 + 3, obj="", parent=current_node)
        count += 1
        current_path.append(current_node.obj)
        i1, i2 = current_node.obj
        if word[i1] < word[i2]:
            current_node = current_node.children[0]
        elif word[i1] == word[i2]:
            current_node = current_node.children[1]
        else:
            current_node = current_node.children[2]

    current_fuzzy_node = fuzzy_tree.root
    current_fuzzy_path = []
    count = 0
    while isinstance(current_fuzzy_node.obj, list):
        count += 1
        current_fuzzy_path.append(current_fuzzy_node.obj)
        i1, i2 = current_fuzzy_node.obj
        if word[i1] < word[i2]:
            current_fuzzy_node = current_fuzzy_node.children[0]
        elif word[i1] == word[i2]:
            current_fuzzy_node = current_fuzzy_node.children[1]
        else:
            current_fuzzy_node = current_fuzzy_node.children[2]

    print("Fuzzy: {} ({})".format(current_fuzzy_path, 'r={}'.format(current_fuzzy_node.obj)))
    print("New Alg.: {} ({})".format(current_path, 'r={}'.format(current_node.obj)))