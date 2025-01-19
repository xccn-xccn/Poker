import random
from r_lists import strength, card_values


def pre_flop(hand, bb_to_call):
    c1, c2 = hand
    suited = c1[1] == c2[1]

    i1, i2 = sorted(
        (14 - card_values[c1[0]], 14 - card_values[c2[0]]), reverse=not suited
    )

    s = strength[i1][i2]

    if s > 1 and random.randint(1, 10) > 3:
        return 3
    elif s > 1 or s > 0.5:
        return 2
    return 1

if __name__ == "__main__":
    pre_flop(("AD", "AH"))
    pre_flop(("AH", "KH"))
    pre_flop(("JH", "2D"))
    pre_flop(("JH", "2H"))

