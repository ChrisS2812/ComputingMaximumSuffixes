import copy
import os
import time
from os import listdir
from os.path import isfile, join
from pathlib import Path

from anytree import LevelOrderIter, PreOrderIter, Node
from anytree.exporter import JsonExporter, DotExporter
from anytree.importer import JsonImporter


class Util:
    knownTn = {1: 0, 2: 1, 3: 2, 4: 3, 5: 5, 6: 6, 7: 7, 8: 8}

    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.comp_pairs = self.generate_all_comp_pairs()
        self.base_dir = "N{}M{}".format(n, m)
        self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
        self.SAVE_INTERVAL = 3600  # 1 hour
        self.LAST_SAVE = int(time.time())

    def create_dirs(self):
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    # Duval's algorithm for finding the index of maximum suffix
    @staticmethod
    def max_suffix_duval(word):
        r = 0
        s = 1
        m = 1
        n = len(word)
        M = {1: 1}
        while s < n:
            if word[s] < word[s - m]:
                s = s + 1
                m = s - r
                M[m] = m
            elif word[s] == word[s - m]:
                s = s + 1
                M[s - r] = m
            else:
                d = (s - r) % m
                if d > 0:
                    r = s - d
                    m = M.get(d)
                else:
                    r = s
                    s += 1
                    m = 1
        return r

    # Compute all possible pairs of indices that can be compared
    def generate_all_comp_pairs(self):
        comp_pairs = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                comp_pairs.append([i, j])
        return comp_pairs

    # Create all possible words for a given n
    def generate_all_words(self):
        orders = [[{1}]]
        for i in range(2, self.n+1):
            new_orders = []
            for order in orders:
                # insert new index between each possible rank
                for j in range(len(order) + 1):
                    c = copy.deepcopy(order)
                    c.insert(j, {i})
                    new_orders.append(c)
                # Add new index to each possible rank
                for j, _ in enumerate(order):
                    c = copy.deepcopy(order)
                    c[j].add(i)
                    new_orders.append(c)
            orders = new_orders

        words = []
        for order in orders:
            word = ['x' for _ in range(self.n)]
            for i, set in enumerate(order):
                for index in set:
                    word[index-1] = str(i)
            word = "".join(word)
            words.append(word)

        # Create the correct maximum suffix index for each relevant word and save it together with word in tuple
        result = [[] for _ in range(self.n)]
        for w in words:
            ms = Util.max_suffix_duval(w)
            result[ms].append(w)

        return result

    def divide_words(self, comp, words):
        smaller_list = [[] for _ in range(self.n)]
        equal_list = [[] for _ in range(self.n)]
        bigger_list = [[] for _ in range(self.n)]
        i1, i2 = comp
        for r, list in enumerate(words):
            for word in list:
                if word[i1] < word[i2]:
                    smaller_list[r].append(word)
                elif word[i1] == word[i2]:
                    equal_list[r].append(word)
                else:
                    bigger_list[r].append(word)
        return bigger_list, equal_list, smaller_list

    # Helping function that checks whether a word in a given tree is valid
    def check_validity_of_word(self, current_node, word, r):
        while True:
            if current_node.obj == "":
                current_node.obj = r
                return True

            elif isinstance(current_node.obj, int):
                if current_node.obj != r:
                    return False
                else:
                    return True
            else:
                if len(current_node.children) == 0:
                    Node(current_node.name * 3 + 1, obj="", parent=current_node)
                    Node(current_node.name * 3 + 2, obj="", parent=current_node)
                    Node(current_node.name * 3 + 3, obj="", parent=current_node)

                i1, i2 = current_node.obj
                c1 = word[i1]
                c2 = word[i2]
                if c1 < c2:
                    current_node = current_node.children[0]
                elif c1 == c2:
                    current_node = current_node.children[1]
                else:
                    current_node = current_node.children[2]


    # Helping function that computes for a list of previously executed comparison and a new (current) comparison
    # whether, after carrying out the new comparison, any other comparisons can be deduced transitively
    @staticmethod
    def compute_transitive_dependencies(previous_comps, current_comp):
        result = []
        (cc1, cc2), cr = current_comp
        for (pc1, pc2), pr in previous_comps:
            # find a pair for a transitive relation (if it exists)
            trans_pair = -1
            case = -1
            if cc1 == pc1:
                # (i,j) and (i,k)
                trans_pair = [cc2, pc2]  # (j,k)
                case = 1
            elif cc2 == pc2:
                # (i,j) and (k,j)
                trans_pair = [cc1, pc1]  # (i,k)
                case = 2
            elif cc1 == pc2:
                # (i,j) and (k,i):
                trans_pair = [cc2, pc1]  # (j,k)
                case = 3
            elif cc2 == pc1:
                # (i,j) and (j,k):
                trans_pair = [cc1, pc2]  # (i,k)
                case = 4

            if trans_pair != -1:
                # found one!
                # call c the index from current comparison and p the index from previous comparison
                if cr == '=' and pr == '=':
                    # cc1=cc2 and pp1=pp2 => c = p
                    result.append((trans_pair, '='))
                elif cr == '=' and pr == '<':
                    # cc1=ccc2 and pp1<pp2
                    if case in [1, 4]:
                        result.append((trans_pair, '<'))
                    elif case in [2, 3]:
                        result.append((trans_pair, '>'))
                elif cr == '=' and pr == '>':
                    # cc1=ccc2 and pp1>pp2
                    if case in [1, 4]:
                        result.append((trans_pair, '>'))
                    elif case in [2, 3]:
                        result.append((trans_pair, '<'))
                elif cr == '<' and pr == '=':
                    # cc1<ccc2 and pp1=pp2
                    if case in [1, 3]:
                        result.append((trans_pair, '>'))
                    elif case in [2, 4]:
                        result.append((trans_pair, '<'))
                elif cr == '>' and pr == '=':
                    # cc1>ccc2 and pp1=pp2
                    if case in [1, 3]:
                        result.append((trans_pair, '<'))
                    elif case in [2, 4]:
                        result.append((trans_pair, '>'))
                elif cr == '<' and pr == '>':
                    # cc1<ccc2 and pp1>pp2
                    if case == 1:
                        result.append((trans_pair, '>'))
                    elif case == 2:
                        result.append((trans_pair, '<'))
                elif cr == '>' and pr == '<':
                    # cc1>ccc2 and pp1<pp2
                    if case == 1:
                        result.append((trans_pair, '<'))
                    elif case == 2:
                        result.append((trans_pair, '>'))
                elif cr == '<' and pr == '<':
                    # cc1<ccc2 and pp1<pp2
                    if case == 3:
                        result.append((trans_pair, '>'))
                    elif case == 4:
                        result.append((trans_pair, '<'))
                elif cr == '>' and pr == '>':
                    # cc1>ccc2 and pp1>pp2
                    if case == 3:
                        result.append((trans_pair, '<'))
                    elif case == 4:
                        result.append((trans_pair, '>'))

        # Clean up results - it is expected that smaller index is always at the first place
        new_result = []
        for res in result:
            if res[0][0] <= res[0][1]:
                new_result.append(res)
                continue
            else:
                new_tuple = [res[0][1], res[0][0]]
                if res[1] == '=':
                    new_result.append((new_tuple, '='))
                elif res[1] == '<':
                    new_result.append((new_tuple, '>'))
                else:
                    new_result.append((new_tuple, '<'))
        return new_result

    @staticmethod
    def filter_comps_for_relevant_suffix(comps, first_rel_char, prev_comps):
        while True:
            if [c for c in prev_comps if c[0][0] == first_rel_char and c[1] == '<']:
                comps = [c for c in comps if c[0] != first_rel_char]
                first_rel_char += 1
            else:
                return comps, first_rel_char

    @staticmethod
    def append_known_decision_tree(current_node, first_rel_char, subword_length_left):
        load_util = Util(subword_length_left, Util.knownTn[subword_length_left])
        for root_comp in load_util.comp_pairs:
            subtree = load_util.load_working_tree(root_comp)
            if subtree is not None:
                # update subtree to match indices of current word and remove deprecated r-values
                for node in PreOrderIter(subtree):
                    if not node.is_leaf:
                        node.obj = [node.obj[0] + first_rel_char, node.obj[1] + first_rel_char]
                    else:
                        node.obj = ""

                current_node.obj = subtree.obj
                current_node.children = (subtree.children[0], subtree.children[1], subtree.children[2])

                # fix naming which is used as indices
                for node in LevelOrderIter(current_node):
                    if node.children:
                        node.children[0].name = node.name * 3 + 1
                        node.children[1].name = node.name * 3 + 2
                        node.children[2].name = node.name * 3 + 3
                return

    # Helping function that regularly saves current state of algorithm (i.e. the current tree)
    # to a file from which it can be reloaded.
    def save_current_graph(self, root, is_final=False):
        self.create_dirs()
        ts = int(time.time())
        if is_final:
            json_filename = "{}_final.json".format(root.obj)
            dot_filename = "{}_final.dot".format(root.obj)
            json_path = os.path.join(self.checkpoint_dir, json_filename)
            dot_filepath = os.path.join(self.checkpoint_dir, dot_filename)

            with open(json_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)

            DotExporter(root, nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_dotfile(dot_filepath)

        elif ts - self.LAST_SAVE >= self.SAVE_INTERVAL:
            json_filename = "{}_{}.json".format(root.obj, ts)
            json_path = os.path.join(self.checkpoint_dir, json_filename)

            with open(json_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)
            self.LAST_SAVE = ts

    def is_already_finished(self, root_comp):
        self.create_dirs()
        return '{}_final.json'.format(root_comp) in listdir(self.checkpoint_dir)

    # Helping function that loads current state of algorithm (i.e. the current tree)
    # from a file in json format
    def load_alg_from_checkpoint(self, root_comp):
        self.create_dirs()
        chkpnt_files = [f for f in listdir(self.checkpoint_dir) if isfile(join(self.checkpoint_dir, f))
                        and f.startswith(str(root_comp))]

        if not chkpnt_files:
            return None

        chkpnt_files.sort()
        most_recent_checkpoint = chkpnt_files[-1]

        path_to_most_recent_checkpoint = os.path.join(self.checkpoint_dir, most_recent_checkpoint)

        with open(path_to_most_recent_checkpoint, 'r') as f:
            root = JsonImporter().read(f)

        return root

    def load_working_tree(self, root_comp):
        self.create_dirs()
        alg_file = os.path.join(self.base_dir, '{}.json'.format(root_comp))

        if os.path.exists(alg_file):
            with open(alg_file, 'r') as f:
                root = JsonImporter().read(f)

                return root

    @staticmethod
    def load_fuzzy_tree(n):
        alg_file = os.path.join('Fuzzy', '{}.json'.format(n))

        if os.path.exists(alg_file):
            with open(alg_file, 'r') as f:
                root = JsonImporter().read(f)

                return root

    def check_valid(self, root):
        for l in root.leaves:
            l.obj = ""
        if root is not None:
            words_with_max_suffix = self.generate_all_words()
            for r, words in enumerate(words_with_max_suffix):
                for word in words:
                    if not self.check_validity_of_word(root, word, r):
                        print("Tree for {} Not verified - failed for word {} ".format(root.obj, word))
                        return False
                    elif word == words_with_max_suffix[-1][0]:
                        print("Found Algorithm with root value {} for n={}, m={}".format(root.obj, self.n, self.m))
                        return True

    def save_algorithm(self, root, filename=None):
        self.create_dirs()
        if root is not None:
            print(len(root.descendants)+1)
        # stop if no algorithm was found or resulting graph was already saved before
        if root is None or (filename is None and '{}.json'.format(root.obj) in listdir(self.base_dir)):
            return

        # Verify (fill in correct r-values in tree on the way in order to pretty print it)
        if self.check_valid(root):
            if filename is None:
                filename = '{}'.format(root.obj)

            json_path = os.path.join(self.base_dir, "{}.json".format(filename))
            with open(json_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)

        #clean up and make indices start at 1 for dotfiles and images
        self.clean_up_final_tree(root)

        for node in list(LevelOrderIter(root)):
            if isinstance(node.obj, list):
                node.obj = [node.obj[0]+1, node.obj[1]+1]

            elif isinstance(node.obj, int):
                node.obj += 1

        DotExporter(root, nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_dotfile(
            "{}/{}.dot".format(self.base_dir, filename))


        if self.n < 7:
            DotExporter(root, nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_picture(
                "{}/{}.png".format(self.base_dir, filename))

    @staticmethod
    def clean_up_final_tree(root):
        # clean up tree by removing unnecessary subtrees
        all_nodes = list(LevelOrderIter(root))
        all_nodes.reverse()
        for node in all_nodes:
            if not node.is_leaf:
                # delete all children if they are all empty
                if node.children[0].obj == "" and node.children[1].obj == "" and node.children[2].obj == "":
                    node.children = ()

                # move r-value to parent, if all children have the same r-value

                elif isinstance(node.children[0].obj, int) and node.children[0].obj == node.children[1].obj and \
                        node.children[1].obj == node.children[2].obj:
                    node.obj = node.children[0].obj
                    node.children = ()

                # move r-value to parent if it is only present at one of three children; remove children afterwards
                elif isinstance(node.children[0].obj, int) and node.children[1].obj == "" and \
                        node.children[2].obj == "":
                    node.obj = node.children[0].obj
                    node.children = ()
                elif isinstance(node.children[1].obj, int) and node.children[0].obj == "" and \
                        node.children[2].obj == "":
                    node.obj = node.children[1].obj
                    node.children = ()
                elif isinstance(node.children[2].obj, int) and node.children[0].obj == "" and \
                        node.children[1].obj == "":
                    node.obj = node.children[2].obj
                    node.children = ()

        # fix names for current print
        index_buffer = 0
        for node in LevelOrderIter(root):
            node.name = index_buffer
            index_buffer += 1
