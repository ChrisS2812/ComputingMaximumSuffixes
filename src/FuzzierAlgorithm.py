from pprint import pprint

import networkx as nx
from python_algorithms.basic.union_find import UF

from src.Util import Util


def compute_fuzzier(word):
    n = len(word)
    count = 0
    cc = UF(n)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    max_positions = {0}
    max_value = word[0]
    unconsidered_positions = [i for i in range(n)]

    i = 0
    j = 2
    unconsidered_positions.remove(0)
    unconsidered_positions.remove(2)

    # Step 1: explore
    while cc.count() > 1:
        mp_list = list(max_positions)
        if cc.count() <= 3 and len(max_positions) > 1 and (mp_list[1] - mp_list[0]) > 1:
            i = mp_list[0] + 1
            j = mp_list[1] + 1

            while True:
                if j == n - 1 or i == mp_list[1]:
                    max_positions = {mp_list[0]}
                    i = mp_list[0]
                    if len(unconsidered_positions) > 0:
                        j = unconsidered_positions[len(unconsidered_positions) // 2]
                        unconsidered_positions.remove(j)
                    elif cc.count() > 1:
                        for new_index in range(n):
                            if cc.find(new_index) != cc.find(i):
                                j = new_index
                                break
                    break
                count += 1
                if i in unconsidered_positions:
                    unconsidered_positions.remove(i)
                if j in unconsidered_positions:
                    unconsidered_positions.remove(j)
                cc.union(i, j)
                if word[i] < word[j]:
                    max_positions = {mp_list[1]}
                    j = mp_list[1]
                    if len(unconsidered_positions) > 0:
                        i = unconsidered_positions[len(unconsidered_positions) // 2]
                        unconsidered_positions.remove(i)
                    elif cc.count() > 1:
                        for new_index in range(n):
                            if cc.find(new_index) != cc.find(j):
                                i = new_index
                                break
                elif word[i] > word[j]:
                    max_positions = {mp_list[0]}
                    i = mp_list[0]
                    if len(unconsidered_positions) > 0:
                        j = unconsidered_positions[len(unconsidered_positions) // 2]
                        unconsidered_positions.remove(j)
                    elif cc.count() > 1:
                        for new_index in range(n):
                            if cc.find(new_index) != cc.find(i):
                                j = new_index
                                break
                else:
                    i += 1
                    j += 1

        else:
            count += 1
            cc.union(i, j)
            if word[i] < word[j]:
                G.add_edge(i, j)
                if word[j] > max_value:
                    max_value = word[j]
                    max_positions = {j}
                if len(unconsidered_positions) > 0:
                    i = unconsidered_positions[len(unconsidered_positions) // 2]
                    unconsidered_positions.remove(i)
                else:
                    for new_index in range(n):
                        if cc.find(new_index) != j:
                            i = new_index
                            break

            elif word[i] > word[j]:
                G.add_edge(j, i)
                if word[i] > max_value:
                    max_value = word[i]
                    max_positions = {i}
                if len(unconsidered_positions) > 0:
                    j = unconsidered_positions[len(unconsidered_positions) // 2]
                    unconsidered_positions.remove(j)
                elif cc.count() > 1:
                    for new_index in range(n):
                        if cc.find(new_index) != cc.find(i):
                            j = new_index
                            break
            else:
                G.add_edge(i, j)
                G.add_edge(j, i)
                if word[i] >= max_value:
                    if i != n-1:
                        max_positions.add(i)
                    if j != n-1:
                        max_positions.add(j)
                if len(unconsidered_positions) > 0:
                    i = unconsidered_positions[0]
                    unconsidered_positions.remove(i)
                elif cc.count() > 1:
                    for new_index in range(n):
                        if cc.find(new_index) != cc.find(j):
                            i = new_index
                            break

    if len(max_positions) == 1:
        return max_positions.pop(), count

    # Step 2 find max suffix from max occurences
    else:
        mp_list = list(set(max_positions))
        mp_list.sort()
        mp_candidates = [mp_list[0]]

        longest_streak = 1
        current_streak = 1
        for i in range(len(mp_list) - 1):
            if mp_list[i + 1] - mp_list[i] == 1:
                # two consecutive maxima
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    mp_candidates = [mp_list[i - current_streak + 2]]
                elif current_streak == longest_streak:
                    mp_candidates.append(mp_list[i - current_streak + 2])
            else:
                current_streak = 1
                if current_streak == longest_streak:
                    mp_candidates.append(mp_list[i + 1])

        if len(mp_candidates) == 1:
            return mp_candidates.pop(), count
        elif mp_candidates[-1] == n - longest_streak:
            mp_candidates.remove(n - longest_streak)
        while len(mp_candidates) > 1:
            count += 1
            i = mp_candidates.pop()
            j = mp_candidates.pop()
            if word[i + 1] > word[j + 1]:
                G.add_edge(j + 1, i + 1)
                mp_candidates.append(i)
            elif word[i + 1] < word[j + 1]:
                G.add_edge(i + 1, j + 1)
                mp_candidates.append(j)
            else:
                return j, count
        return mp_candidates.pop(), count


nr_comps = {}

for r, words in enumerate(Util(6, -1).generate_all_words()):
    for word in words:
        (r_fuzzier, count) = compute_fuzzier(word)
        if r_fuzzier != r:
            print("Fuzzier Algorithm failed for {} [r={}, r_actual={}]".format(word, r_fuzzier, r))
        if count not in nr_comps:
            nr_comps[count] = 1
        else:
            nr_comps[count] += 1
        if count == 8:
            print(word)
pprint(nr_comps)
