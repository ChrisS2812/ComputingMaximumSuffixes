import copy

from src.Util import Util

def compute_max_prefix_find_max(word):
    i = 0
    leading_max_values_of_maximum = 1
    leading_max_values_current = 0
    max_is_expanding = True
    max_indices = [0]

    # First n-1 comparisons: find maxima
    for j in range(1, len(word)):
        if word[i] > word[j]:
            max_is_expanding = False
            leading_max_values_current = 0
        elif word[i] < word[j]:
            i = j
            max_indices = [i]
            max_is_expanding = True
            leading_max_values_current = 1
            leading_max_values_of_maximum = 1
        else:
            if max_is_expanding:
                leading_max_values_of_maximum += 1
            else:
                leading_max_values_current += 1
            if leading_max_values_current == leading_max_values_of_maximum:
                max_indices.append(j - leading_max_values_current + 1)

            elif leading_max_values_current > leading_max_values_of_maximum:
                i = j - leading_max_values_current + 1
                max_indices = [i]
                leading_max_values_of_maximum = leading_max_values_current
                max_is_expanding = True

    # last comparisons
    max_suffix_candidates = copy.deepcopy(max_indices)
    while len(max_suffix_candidates) > 1:
        c1 = max_suffix_candidates[0]
        c2 = max_suffix_candidates[1]
        i1 = c1
        i2 = c2
        while True:
            if i1 + leading_max_values_of_maximum in max_indices:
                max_suffix_candidates.remove(c2)
                break
            if i2 + leading_max_values_of_maximum in max_indices:
                max_suffix_candidates.remove(c1)
                break
            if i2 + leading_max_values_of_maximum == len(word):
                max_suffix_candidates.remove(c2)
                break
            if word[i1 + leading_max_values_of_maximum] < word[i2 + leading_max_values_of_maximum]:
                max_suffix_candidates.remove(c1)
                break
            if word[i1 + leading_max_values_of_maximum] > word[i2 + leading_max_values_of_maximum]:
                max_suffix_candidates.remove(c2)
                break
            i1 += 1
            i2 += 1
    return max_suffix_candidates[0]


for word, r in Util(7, -1).generate_all_word_with_max_suffix():
    r_max = compute_max_prefix_find_max(word)
    if r_max != r:
        print("Find Max Algorithm failed for {} [r={}, r_actual={}".format(word, r_max, r))
