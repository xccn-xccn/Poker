import random
from time import perf_counter
from math import log



def strength_index(c1, c2):
    return sorted(
        (14 - card_values[c1[0]], 14 - card_values[c2[0]]), reverse=c1[1] != c2[1]
    )


def pre_strength(c1, c2):
    i1, i2 = strength_index(c1, c2)
    return strengths[i1][i2]


def get_min_hand(strength):
    pass


strengths = [
    [
        float("inf"),
        3.44,
        2.80,
        2.36,
        2.06,
        1.65,
        1.52,
        1.39,
        1.29,
        1.38,
        1.29,
        1.20,
        1.10,
    ],
    [3.00, 6.58, 2.26, 1.98, 1.77, 1.40, 1.19, 1.10, 1.03, 0.95, 0.86, 0.80, 0.74],
    [2.14, 1.62, 5.48, 1.82, 1.67, 1.32, 1.10, 0.89, 0.84, 0.76, 0.70, 0.64, 0.59],
    [1.66, 1.33, 1.20, 4.53, 1.62, 1.28, 1.06, 0.83, 0.63, 0.58, 0.52, 0.47, 0.42],
    [1.35, 1.11, 1.03, 1.01, 3.81, 1.32, 1.11, 0.87, 0.66, 0.47, 0.43, 0.39, 0.35],
    [0.94, 0.74, 0.68, 0.67, 0.72, 3.13, 1.11, 0.91, 0.70, 0.47, 0.35, 0.32, 0.29],
    [0.81, 0.56, 0.51, 0.50, 0.53, 0.54, 2.59, 0.98, 0.82, 0.59, 0.38, 0.27, 0.24],
    [0.70, 0.49, 0.38, 0.36, 0.38, 0.41, 0.44, 2.14, 0.89, 0.69, 0.48, 0.30, 0.19],
    [0.62, 0.43, 0.33, 0.25, 0.26, 0.28, 0.32, 0.36, 1.81, 0.79, 0.61, 0.40, 0.23],
    [0.67, 0.39, 0.30, 0.22, 0.17, 0.17, 0.21, 0.26, 0.30, 1.48, 0.71, 0.53, 0.33],
    [0.59, 0.33, 0.25, 0.18, 0.13, 0.07, 0.10, 0.14, 0.19, 0.24, 1.22, 0.45, 0.28],
    [0.53, 0.29, 0.21, 0.14, 0.09, 0.04, 0.02, 0.05, 0.08, 0.14, 0.08, 1.01, 0.23],
    [0.45, 0.25, 0.17, 0.10, 0.06, 0.01, 0.01, 0.01, 0.01, 0.04, 0.01, 0.01, 0.87],
]

card_values = {1: "A"}
for v, k in enumerate("23456789TJQKA", 2):
    card_values[k] = v
    card_values[v] = k

flatt_strengths = sorted([a for b in strengths for a in b], reverse=True)
deck = [c + s for s in "CSHD" for c in "23456789TJQKA"]
all_p_hands = [
    (c1, c2)
    for c1 in deck
    for c2 in deck
    if card_values[c1[0]] > card_values[c2[0]] or c1[0] == c2[0] and c1[1] > c2[1]
]
sorted_hands = sorted(all_p_hands, key=lambda x: pre_strength(*x), reverse=True)
strengths_to_index = {pre_strength(*x): i for i, x in enumerate(sorted_hands)}

def sort_hole(c1, c2):
    return tuple(sorted((c1, c2), key=lambda x: (card_values[x[0]], x[1]), reverse=True))
def get_ps_index(c_range, m_strength):
    l, h = 0, len(c_range) - 1

    while l <= h:
        m = l + (h - l) // 2

        t_strength = pre_strength(*c_range[m])

        if t_strength < m_strength:
            h = m - 1
        elif t_strength > m_strength:
            l = m + 1
        else:
            return l
        # 4, 3, 2, 1     2.5

    return m


def get_ps_strength(m_strength, minimum=True):
    l, h = 0, len(flatt_strengths) - 1

    while l <= h:
        m = l + (h - l) // 2

        t_strength = flatt_strengths[m]

        if t_strength < m_strength:
            h = m - 1
        elif t_strength > m_strength:
            l = m + 1
        else:
            return t_strength
        # 4, 3, 2, 1     2.5

    return flatt_strengths[m - 1] if minimum else flatt_strengths[m]


def main():

    # print(sorted_hands[get_ps_index(sorted_hands, 3.00)])
    # print(get_ps_strength(0.2, minimum=False))
    print(sort_hole("AH", "AD"))
    print(sorted_hands[:8])
    pass

    


if __name__ == "__main__":
    # l = list(range(1_000_000))
    # random.shuffle(l)
    start = perf_counter()

    # print(list(map(lambda x: round(x**2, 3), s)))

    # for s in strengths:
    #     print(list(map(lambda x: round(x**3 * 3, 3), s)))
    # list(sorted(l))
    main()

    print(f"Time taken: {(perf_counter() - start) *1000} miliseconds")
