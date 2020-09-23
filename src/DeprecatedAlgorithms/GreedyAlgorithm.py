from src.Util import Util

def compute_max_prefix_greedy(word):
    r = 0
    i = 1
    leading_max_values_of_maximum = 1
    leading_max_values_current = 1
    max_is_expanding = True

    while i < len(word):
        if word[r] < word[i]:
            r = i
            i = r+1
            leading_max_values_of_maximum = 1
            leading_max_values_current = 0
            max_is_expanding = True
        elif word[r] > word[i]:
            i += 1
            leading_max_values_current = 0
            max_is_expanding = False

        else:
            leading_max_values_current += 1
            i += 1

            if max_is_expanding:
                leading_max_values_of_maximum += 1
                continue

            if leading_max_values_current == leading_max_values_of_maximum:
                j = r + leading_max_values_of_maximum - 1
                k = i - 1

                while True:
                    j += 1
                    k += 1

                    if k >= len(word):
                        return r

                    if word[j] > word[k]:
                        break
                    elif word[j] < word[k]:
                        r = i - leading_max_values_current
                        break

            if leading_max_values_current > leading_max_values_of_maximum:
                r = i - leading_max_values_current
                leading_max_values_of_maximum = leading_max_values_current
                leading_max_values_current = 0
                i = r + leading_max_values_of_maximum
                max_is_expanding = True
    return r

for word, r in Util(6, -1).generate_all_words():
    r_sandwich = compute_max_prefix_greedy(word)
    if r_sandwich != r:
        print("Greedy Algorithm failed for {} [r={}, r_actual={}".format(word, r_sandwich, r))


