import itertools
import os
import time
from os import listdir
from os.path import isfile
from pathlib import Path

from anytree import LevelOrderIter
from anytree.exporter import JsonExporter
from anytree.importer import JsonImporter


class Util:
    def __init__(self, n, m):
        self.N = n
        self.M = m
        self.base_dir = "N{}M{}".format(n, m)
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        self.SAVE_INTERVAL = 1800  # 30 minutes
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

    # Create all possible words for a given N
    def generate_all_word_with_max_suffix(self):
        # List of all words
        all_words = list(itertools.product(range(self.N), repeat=self.N))

        # Reduce this to list of relevant words by defining two words as equivalent if all its pairwise comparisons have
        # the same result
        comp_result_2_word = {}
        for w in all_words:
            comparisons = ""
            for i in range(self.N):
                for j in range(i + 1, self.N):
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

        # Helping function that computes the path of of a given word in a given decision tree in the form:

    # * (n_1,...,n_m) where n_i represents the id of the i'th node
    def compute_path_for_word(self, alg, word):
        current_index = 0
        path = []
        while current_index < len(alg):
            path.append(current_index)
            if self.is_leaf(current_index):
                break
            i1, i2 = alg[current_index].obj
            c1 = word[i1]
            c2 = word[i2]
            if c1 < c2:
                current_index = current_index * 3 + 1
            elif c1 == c2:
                current_index = current_index * 3 + 2
            else:
                current_index = current_index * 3 + 3
        return path

    # Helping function that computes (all) decision-tree-independent path representation on which a given index lies.
    # A path is a string of the form:
    # * c_1r_1c_2_r_2...c_M
    # where c_i represents a comparison and r_i the result of this comparison ("<", "=", or ">")
    def compute_path_repr_for_index(self, alg, index):
        if self.is_leaf(index=index):
            return self.compute_path_repr_for_index(alg, (index - 1) // 3)
        if self.is_last_comp(index=index):
            # start at lowest comparison node (the last node is not important for blacklisted paths)
            re = str(alg[index].obj)
            while index != 0:
                mod = index % 3
                if mod == 0:
                    re = ">" + re
                elif mod == 1:
                    re = "<" + re
                else:
                    re = "=" + re
                index = (index - 1) // 3
                re = str(alg[index].obj) + re
            return [re]
        else:
            result = []
            # Append paths for all children
            result.extend(self.compute_path_repr_for_index(alg, index * 3 + 1))
            result.extend(self.compute_path_repr_for_index(alg, index * 3 + 2))
            result.extend(self.compute_path_repr_for_index(alg, index * 3 + 3))
            return result

    # Helping function that decides whether a node at a given index is a leaf or not.
    def is_leaf(self, index):
        if self.M < 1:
            return True

        last_non_leaf_index = -1
        for i in range(0, self.M):
            last_non_leaf_index += 3 ** i
        if index <= last_non_leaf_index:
            return False
        else:
            return True

    # Helping function that decides whether a node at a given index represents the last comparison
    def is_last_comp(self, index):
        if self.M < 1:
            return False
        if self.M == 2:
            if index == 0:
                return True
            else:
                return False

        if self.is_leaf(index):
            return False

        last_non_last_comp_index = -1
        for i in range(0, self.M - 1):
            last_non_last_comp_index += 3 ** i

        if index > last_non_last_comp_index:
            return True
        else:
            return False

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
                trans_pair = (cc2, pc2)  # (j,k)
                case = 1
            elif cc2 == pc2:
                # (i,j) and (k,j)
                trans_pair = (cc1, pc1)  # (i,k)
                case = 2
            elif cc1 == pc2:
                # (i,j) and (k,i):
                trans_pair = (cc2, pc1)  # (j,k)
                case = 3
            elif cc2 == pc1:
                # (i,j) and (j,k):
                trans_pair = (cc1, pc2)  # (i,k)
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
                new_tuple = (res[0][1], res[0][0])
                if res[1] == '=':
                    new_result.append((new_tuple, '='))
                elif res[1] == '<':
                    new_result.append((new_tuple, '>'))
                else:
                    new_result.append((new_tuple, '<'))
        return new_result

    # Helping function that regularly saves current state of algorithm (i.e. the current tree)
    # to a file from which it can be reloaded.
    def save_current_graph(self, root):
        ts = int(time.time())
        if ts - self.LAST_SAVE >= self.SAVE_INTERVAL:
            filename = "{}_{}.json".format(root.obj, ts)
            final_path = os.path.join(self.checkpoint_dir, filename)

            with open(final_path, 'w') as f:
                JsonExporter(indent=2).write(root, f)
            self.LAST_SAVE = ts

    # Helping function that loads current state of algorithm (i.e. the current tree)
    # from a file in json format
    def load_alg_from_checkpoint(self, root_comp):
        from os.path import join
        chkpnt_files = [f for f in listdir(self.checkpoint_dir) if isfile(join(self.checkpoint_dir, f))
                        and f.startswith(str(root_comp))]

        if not chkpnt_files:
            return -1

        chkpnt_files.sort()
        most_recent_checkpoint = chkpnt_files[-1]

        path_to_most_recent_checkpoint = os.path.join(self.checkpoint_dir, most_recent_checkpoint)

        with open(path_to_most_recent_checkpoint, 'r') as f:
            root = JsonImporter().read(f)

        alg = [node for node in LevelOrderIter(root)]
        for node in alg:
            node.obj = tuple(node.obj)

        return alg
