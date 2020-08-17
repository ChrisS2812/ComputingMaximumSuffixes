from src.Util import Util

def compute_max_prefix_sandwich(word):
    r = 0
    i = 0
    j = len(word) - 1

    while i < j:
        if word[i] < word[j]:
            i += 1
            r = j
        elif word[i] > word[j]:
            j -= 1
            r = i
        else:
            if j == i+1:
                r = i
                break
            k = i
            l = j
            while True:
                k += 1
                l += 1
                if l > len(word) - 1:
                    j -= 1
                    r = i
                    break
                if k == j:
                    return i
                if word[k] < word[l]:
                    i += 1
                    r = j
                    break
                if word[k] > word[l]:
                    j -= 1
                    r = i
                    break
    return r

for word, r in Util(7, -1).generate_all_word_with_max_suffix():
    r_sandwich = compute_max_prefix_sandwich(word)
    if r_sandwich != r:
        print("Sandwich Algorithm failed for {} [r={}, r_actual={}".format(word, r_sandwich, r))


