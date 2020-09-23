from anytree import Node

from Util import Util

n = 8
m = 8

NPLUSONE_UTIL = Util(n, m)

COMP_LEFT_FOR_WHICH_CHANGE_ALLOWED = 4

def extend_tree(root, words, m_left):
    if m_left == 0:
        return False

    if m_left <= COMP_LEFT_FOR_WHICH_CHANGE_ALLOWED or (not isinstance(root.obj, list) or isinstance(root.obj, tuple)):
        # try to find new comparison that "fixes" current
        for c in NPLUSONE_UTIL.generate_all_comp_pairs():
            root.obj = c
            bigger_list, equal_list, smaller_list = NPLUSONE_UTIL.divide_words(c, words)

            if len([l for l in bigger_list if len(l) > 0]) < 2 and \
                    len([l for l in equal_list if len(l) > 0]) < 2 and \
                    len([l for l in smaller_list if len(l) > 0]) < 2:
                return True

            if len(root.children) == 0:
                Node(root.name * 3 + 1, obj="", parent=root)
                Node(root.name * 3 + 2, obj="", parent=root)
                Node(root.name * 3 + 3, obj="", parent=root)

            if extend_tree(root.children[0], smaller_list, m_left-1) and \
                extend_tree(root.children[1], equal_list, m_left-1) and \
                extend_tree(root.children[2], bigger_list, m_left-1):
                return True

    else:
        bigger_list, equal_list, smaller_list = NPLUSONE_UTIL.divide_words(root.obj, words)
        if len(root.children) == 0:
            Node(root.name * 3 + 1, obj="", parent=root)
            Node(root.name * 3 + 2, obj="", parent=root)
            Node(root.name * 3 + 3, obj="", parent=root)
        return extend_tree(root.children[0], smaller_list, m_left-1) and extend_tree(root.children[1],
                                                                           equal_list, m_left-1) and extend_tree(root.children[2],
                                                                                                       bigger_list, m_left-1)


words = NPLUSONE_UTIL.generate_all_words()

fuzzy_tree = Util.load_fuzzy_tree(n-1)
if extend_tree(fuzzy_tree, words, m):
    print("Found extension for Fuzzy")
else:
    print("Found NO extension for Fuzzy")

for comp in NPLUSONE_UTIL.generate_all_comp_pairs():
    root = Util(n-1, m-1).load_working_tree(comp)
    if root is not None:
        if (extend_tree(root, words, m)):
            print("Found extension for algorithm with root {}".format(comp))
            NPLUSONE_UTIL.save_algorithm(root)
        else:
            print("No extension for root {} found".format(comp))
