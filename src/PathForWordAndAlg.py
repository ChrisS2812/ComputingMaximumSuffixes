from Util import Util

UTIL = Util(8, 8)

tree = UTIL.load_working_tree([0,3])

word = "10403040"

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

print(current_path, 'r={}'.format(current_node.obj))