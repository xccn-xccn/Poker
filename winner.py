from collections import Counter
from functools import cache
from r_lists import card_values


def get_winner(hands, community):
    order = [
        get_straight_flush,
        get_four,
        get_house,
        get_flush,
        get_straight,
        get_three,
        get_2pair,
        get_pair,
        cardValue_sort,
    ]

    cards = [list(h) + community for h in hands]
    best = [[]]
    for f in order:
        for i, player in enumerate(cards):
            finalHand = get_hand(player, f)
            if finalHand:
                if best == [[]]:
                    best = [[finalHand, i]]
                else:
                    best_player = compare_hand(finalHand, best[0][0])
                    if best_player == 1:
                        best = [[finalHand, i]]
                    if best_player == 3:  # draw
                        best.append([finalHand, i])

        if best != [[]]:
            break

    return best


def compare_hand(hand1, hand2):
    for c1, c2 in zip(hand1, hand2):
        v1, v2 = c1[0], c2[0]
        if card_values[v1] > card_values[v2]:
            return 1
        elif card_values[v2] > card_values[v1]:
            return 2

    return 3


def cardValue_sort(x):
    return sorted(x, key=lambda y: card_values[y[0]], reverse=True)


# @cache
def get_hand(cards, f):
    used = f(cards)
    if used == False:
        return False
    remaining = cardValue_sort([c for c in cards if c not in used])

    return used[:5] + remaining[: 5 - len(used)]


def get_same(cards, n):
    c_cards = Counter([c[0] for c in cards])

    pairs = []
    for card, val in c_cards.items():
        if val >= n:
            pairs.append(card)

    output = cardValue_sort([c for c in cards if c[0] in pairs])

    return output if output else False


def get_pair(cards):
    p = get_same(cards, 2)
    return p[:2] if p else False


def get_2pair(cards):
    p = get_same(cards, 2)
    if p == False or len(p) < 4:
        return False
    return p[:4]


def get_three(cards):
    return get_same(cards, 3)


def get_house(cards):
    three = get_three(cards)
    if not three:
        return False
    remaining = [c for c in cards if c not in three]
    pair = get_pair(remaining)

    if not pair:
        return False

    pair = pair[:2]

    if three and pair:
        return three + pair

    return False


def get_four(cards):
    return get_same(cards, 4)


def get_straight(cards, l_5=True):
    copyCards = cards.copy()
    cards = []
    for c in copyCards:
        cards.append((card_values[c[0]], c[1]))
        if c[0] == "A":
            cards.append((1, c[1]))

    cards = sorted(list(set(cards)), key=lambda x: x[0], reverse=True)

    straight = [cards[0]]
    for c1, c2 in zip(cards, cards[1:]):
        v1, v2 = c1[0], c2[0]

        if v1 == v2:
            continue
        elif v1 - v2 == 1:
            straight.append(c2)
        else:
            if len(straight) >= 5:
                break
            straight = [c2]

    if l_5:
        straight = straight[:5]
    return False if len(straight) < 5 else [card_values[v] + s for v, s in straight]


def get_flush(cards, l_5=True):
    cardSuits = [c[1] for c in cards]
    c_cards = Counter(cardSuits)

    most = c_cards.most_common(1)[0]
    if most[1] >= 5:
        suit = most[0]
    else:
        return False

    output = cardValue_sort([c for c in cards if c[1] == suit])
    if l_5:
        output = output[:5]

    return output


def get_straight_flush(cards):
    f_cards = get_flush(cards, l_5=False)

    if not f_cards:
        return False
    s_f_cards = get_straight(f_cards)

    return s_f_cards


def get_best_hand(cards):
    order = [
        get_straight_flush,
        get_four,
        get_house,
        get_flush,
        get_straight,
        get_three,
        get_2pair,
        get_pair,
        cardValue_sort,
    ]

    for f in order:
        if get_hand(cards, f):
            return get_hand(cards, f)


if __name__ == "__main__":
    # print(get_flush(["AC", "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "KD"]))
    # print(get_straight(["AC", "2C", "4C", "5C", "6C", "7C", "8D", "9C", "3D"]))
    # # print(get_pairs(["AC", "2C", "4C", "5C", "6C", "6D", "8D", "9C", "2D"]))
    # print(get_straight_flush(["AC", "2C", "4C", "5C", "6C", "7C", "8D", "9C", "3C"]))
    # print(get_pair(["AC", "2C", "2S", "6C", "6D", "2D"]))
    # print(get_2pair(["AC", "2C", "2S", "6C", "6D", "2D"]))

    print(get_winner([("AH", "JC"), ("AS", "3H")], ["AC", "KS", "7C", "JS", "9D"]))

    # print(get_best_hand(["AC", "2S", "7C", "3S", "9D"]))
