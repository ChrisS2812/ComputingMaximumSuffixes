import networkx as nx
from networkx import has_path

from src.Util import Util


def compute_fuzzier(word):
    unconsidered_indices = list(range(len(word)))
    G = nx.DiGraph()
    G.add_nodes_from(range(len(word)))
    max_positions = {0}
    max_value = word[0]

    i = unconsidered_indices.pop(0)
    j = unconsidered_indices.pop(0)

    while True:
        if word[i] > word[j]:
            if max_value < word[i]:
                max_value = word[i]
                max_positions = {i}
            else:
                max_positions.add(i)
            G.add_edge(j, i)
            if len(unconsidered_indices) == 0:
                break
            j = unconsidered_indices.pop(0)
        elif word[i] < word[j]:
            if max_value < word[j]:
                max_value = word[j]
                max_positions = {j}
            else:
                max_positions.add(j)
            G.add_edge(i, j)
            if len(unconsidered_indices) == 0:
                break
            i = unconsidered_indices.pop(0)
        else:
            max_positions.add(i)
            max_positions.add(j)
            G.add_edge(i, j)
            G.add_edge(j, i)
            if len(unconsidered_indices) == 0:
                break
            if i < j:
                i = unconsidered_indices.pop(0)
            else:
                j = unconsidered_indices.pop(0)

    max_positions = list(max_positions)
    max_positions.sort()

    if len(max_positions) == 1:
        return max_positions.pop()

    space_between_max = [max_positions[i + 1] - max_positions[i] - 1 for i in range(len(max_positions) - 1)]
    new_max_indices = []
    max_lengths = []
    max_prefix_candidates = [i for i in max_positions]
    for i, space in enumerate(space_between_max):
        if space == 0:
            if len(new_max_indices) > 0 and new_max_indices[-1] == max_positions[i] - max_lengths[-1]:
                max_lengths[-1] += 1
            else:
                new_max_indices.append(max_positions[i])
                max_lengths.append(1)
    if new_max_indices:
        max_prefix_candidates = [index for i, index in enumerate(new_max_indices) if max_lengths[i] == max(max_lengths)]

    if len(max_prefix_candidates) > 2 and len(word) - 1 in max_prefix_candidates:
        max_prefix_candidates.remove(len(word) - 1)

    if len(max_lengths) == 0:
        max_lengths = [0 for _ in max_prefix_candidates]

    while len(max_prefix_candidates) > 1:
        i_buffer = max_prefix_candidates[0] + 1 + max_lengths[0]
        j_buffer = max_prefix_candidates[1] + 1 + max_lengths[1]
        while True:
            if (i_buffer in max_positions and j_buffer not in max_positions) or j_buffer == len(word):
                max_prefix_candidates.pop(1)
                max_lengths.pop(1)
                break

            if (j_buffer in max_positions) and (i_buffer not in max_positions):
                max_prefix_candidates.pop(0)
                max_lengths.pop(0)
                break

            if has_path(G, i_buffer, j_buffer) and not has_path(G, j_buffer, i_buffer):
                max_prefix_candidates.pop(0)
                max_lengths.pop(0)
                break
            elif has_path(G, i_buffer, j_buffer) and not has_path(G, j_buffer, i_buffer):
                max_prefix_candidates.pop(1)
                max_lengths.pop(1)
                break
            elif not has_path(G, i_buffer, j_buffer) and not has_path(G, j_buffer, i_buffer):
                if word[i_buffer] < word[j_buffer]:
                    G.add_edge(i_buffer, j_buffer)
                    max_prefix_candidates.pop(0)
                    max_lengths.pop(0)
                    break
                elif word[i_buffer] > word[j_buffer]:
                    G.add_edge(j_buffer, i_buffer)
                    max_prefix_candidates.pop(1)
                    max_lengths.pop(1)
                    break
                else:
                    G.add_edge(i_buffer, j_buffer)
                    G.add_edge(j_buffer, i_buffer)
            i_buffer += 1
            j_buffer += 1

    return max_prefix_candidates.pop()


for word, r in Util(8, -1).generate_all_word_with_max_suffix():
    r_fuzzier = compute_fuzzier(word)
    if r_fuzzier != r:
        print("Fuzzier Algorithm failed for {} [r={}, r_actual={}".format(word, r_fuzzier, r))
