import itertools
import os
import time
from os import listdir
from os.path import isfile, join
from pathlib import Path

import copy
from anytree import LevelOrderIter, PreOrderIter
from anytree.exporter import JsonExporter, DotExporter
from anytree.importer import JsonImporter


class Util:
    knownTn = {1: 0, 2: 1, 3: 2, 4: 3, 5: 5, 6: 6, 7: 7}

    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.comp_pairs = self.generate_all_comp_pairs()
        self.base_dir = "N{}M{}".format(n, m)
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        self.SAVE_INTERVAL = 3600  # 1 hour
        self.LAST_SAVE = int(time.time())

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

    # Create all possible words for a given N
    def generate_all_word_with_max_suffix(self):
        # List of all words
        all_words = list(itertools.product(range(self.n), repeat=self.n))

        # Reduce this to list of relevant words by defining two words as equivalent if all its pairwise comparisons have
        # the same result
        comp_result_2_word = {}
        for w in all_words:
            comparisons = ""
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    c1 = w[i]
                    c2 = w[j]
                    if c1 < c2:
                        comparisons += "<"
                    elif c1 > c2:
                        comparisons += ">"
                    else:
                        comparisons += "="
            if comparisons not in comp_result_2_word:
                comp_result_2_word[comparisons] = w

        rel_words = []

        for entry in comp_result_2_word.values():
            w = ''
            for char in entry:
                w += str(char)
            rel_words.append(w)

        # Create the correct maximum suffix index for each relevant word and save it together with word in tuple
        result = []
        for w in rel_words:
            result.append((w, Util.max_suffix_duval(w)))

        return result

    @staticmethod
    def divide_words(comp, words):
        i1, i2 = comp
        smaller_list = []
        equal_list = []
        bigger_list = []
        for entry in words:
            curr_word = entry[0]
            if curr_word[i1] < curr_word[i2]:
                smaller_list.append(entry)
            elif curr_word[i1] == curr_word[i2]:
                equal_list.append(entry)
            else:
                bigger_list.append(entry)
        return bigger_list, equal_list, smaller_list

    # Helping function that checks whether a word in a given tree is valid
    def check_validity_of_word(self, current_node, word, r):
        while True:
            if not isinstance(current_node.obj, list):
                break
            i1, i2 = current_node.obj
            c1 = word[i1]
            c2 = word[i2]
            if c1 < c2:
                current_node = current_node.children[0]
            elif c1 == c2:
                current_node = current_node.children[1]
            else:
                current_node = current_node.children[2]
        if current_node.obj != "" and current_node.obj != r:
            return False
        else:
            current_node.obj = r
            return True

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
    def find_relevant_subword(comps_smaller_new, first_rel_char1, prev_comps_smaller_new):
        while True:
            if ([first_rel_char1, first_rel_char1 + 1], '<') in prev_comps_smaller_new:
                comps_smaller_new = list(filter(lambda x: x[0] == first_rel_char1, comps_smaller_new))
                first_rel_char1 += 1
            else:
                break
        return comps_smaller_new, first_rel_char1

    @staticmethod
    def create_new_comps(c_new, comps, prev_comps, transitive_smaller):
        comps_smaller_new = copy.deepcopy(comps)
        prev_comps_smaller_new = copy.deepcopy(prev_comps)
        prev_comps_smaller_new.append((c_new, '<'))
        comps_smaller_new.remove(c_new)
        for c, res in [t for t in transitive_smaller if t[0] in comps]:
            comps_smaller_new.remove(c)
            prev_comps_smaller_new.append((c, res))
        return comps_smaller_new, prev_comps_smaller_new

    def append_known_decision_tree(self, current_node, first_rel_char, subword_length_left):
        LOAD_UTIL = Util(subword_length_left, Util.knownTn[subword_length_left])
        for root_comp in self.comp_pairs:
            subtree = LOAD_UTIL.load_working_tree(root_comp)
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

    # Helping function that regularly saves current state of algorithm (i.e. the current tree)
    # to a file from which it can be reloaded.
    def save_current_graph(self, root, is_final=False):
        ts = int(time.time())
        if is_final:
            filename = "{}_final.json".format(root.obj)
            final_path = os.path.join(self.checkpoint_dir, filename)

            with open(final_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)

        elif ts - self.LAST_SAVE >= self.SAVE_INTERVAL:
            filename = "{}_{}.json".format(root.obj, ts)
            final_path = os.path.join(self.checkpoint_dir, filename)

            with open(final_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)
            self.LAST_SAVE = ts

    # Helping function that loads current state of algorithm (i.e. the current tree)
    # from a file in json format
    def load_alg_from_checkpoint(self, root_comp):
        chkpnt_files = [f for f in listdir(self.checkpoint_dir) if isfile(join(self.checkpoint_dir, f))
                        and f.startswith(str(root_comp))]

        if not chkpnt_files:
            return None

        most_recent_checkpoint = '{}_final'.format(root_comp)

        if most_recent_checkpoint not in chkpnt_files:
            chkpnt_files.sort()
            most_recent_checkpoint = chkpnt_files[-1]

        path_to_most_recent_checkpoint = os.path.join(self.checkpoint_dir, most_recent_checkpoint)

        with open(path_to_most_recent_checkpoint, 'r') as f:
            root = JsonImporter().read(f)

        return root

    def load_working_tree(self, root_comp):
        alg_file = os.path.join(self.base_dir, '{}.json'.format(root_comp))

        if os.path.exists(alg_file):
            with open(alg_file, 'r') as f:
                root = JsonImporter().read(f)

                return root

    def save_algorithm(self, root):
        if root is None:
            return
        words_with_max_suffix = self.generate_all_word_with_max_suffix()
        comp = root.obj

        # Verify (fill in correct r-values in tree on the way in order to pretty print it)
        for word, r in words_with_max_suffix:
            if not self.check_validity_of_word(root, word, r):
                print("Not verified - failed for word {} ".format(word))
                DotExporter(root, nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_picture(
                    "{}_fail.png".format(root.obj))
                break

            elif word == words_with_max_suffix[-1][0]:
                print("Found Algorithm with root value {} for n={}, m={}".format(root.obj, self.n, self.m))

                #clean up tree by removing unnecessary subtrees
                all_nodes = list(LevelOrderIter(root))
                all_nodes.reverse()
                for node in all_nodes:
                    if not node.is_leaf:
                        if node.children[0].obj == "" and node.children[1].obj == "" and node.children[2].obj == "":
                            node.obj = ""
                            node.children = ()
                        elif node.children[0].obj != "" and node.children[1].obj == "" and node.children[2].obj == "":
                            node.obj = node.children[0].obj
                            node.children = ()
                        elif node.children[1].obj != "" and node.children[0].obj == "" and node.children[2].obj == "":
                            node.obj = node.children[1].obj
                            node.children = ()
                        elif node.children[2].obj != "" and node.children[0].obj == "" and node.children[1].obj == "":
                            node.obj = node.children[2].obj
                            node.children = ()

                #fix names for current print
                index_buffer = 0
                for node in LevelOrderIter(root):
                    node.name = index_buffer
                    index_buffer += 1

                DotExporter(root, nodeattrfunc=lambda my_node: 'label="{}"'.format(my_node.obj)).to_picture(
                    "{}/{}.png".format(self.base_dir, comp))
                json_path = os.path.join(self.base_dir, "{}.json".format(root.obj))
                with open(json_path, 'w') as f:
                    JsonExporter(indent=2).write(root, f)
