from collections import Counter
from functools import cmp_to_key
from backbone_misc import *
from time import perf_counter
from random import choices
# NOTE functions like get_four will not only select the best quads but all possible quads meaning they cannot be used as kickers (important for 4 card poker)
# TODO check if bug fixed

def get_winner(hands, community):

    cards = [list(h) + community for h in hands]
    best = [[]]
    for f in order:
        for i, player in enumerate(cards):
            finalHand = get_hand(player, f)
            if finalHand:
                if best == [[]]:
                    best = [[finalHand, i]]
                else:
                    best_player = compare_hand_k(finalHand, best[0][0])
                    if best_player == 1:
                        best = [[finalHand, i]]
                    if best_player == 0:  # draw
                        best.append([finalHand, i])

        if best != [[]]:
            break

    return best


def all_hands_ranked(community, known=None, p_hands=None):
    # try to bucket draws and combo draws?

    if known == None:
        known = []
    if p_hands == None:
        p_hands = all_p_hands

    o_hands = []
    buckets = [[] for _ in range(21)]

    for h in p_hands:
        i1, f_hand = get_hand_rank(h, community)
        if h[0] in community + known or h[1] in community + known:
            continue

        buckets[i1].append((h, f_hand))

    for b in buckets:
        o_hands += [
            x
            for x in list(
                sorted(
                    b,
                    key=cmp_to_key(lambda x, y: compare_hand_k(x[1], y[1])),
                    reverse=True,
                )
            )
        ]

    return group_rank(o_hands)


def group_rank_pre(hands):
    final = {hands[0]: 0}
    rank = 0
    for hand1, hand2 in zip(hands, hands[1:]):
        if pre_strength(*hand1) != pre_strength(*hand2):
            rank = len(final)
        final[hand2] = rank

    return final


def group_rank(hands, f=None):
    if f == None:
        f = compare_hand_k
    final = {hands[0][0]: 0}
    rank = 0
    for (_, hand1), (hole2, hand2) in zip(hands, hands[1:]):
        if f(hand1, hand2) != 0:
            rank = len(final)
        final[hole2] = rank

    return final


def all_hands2(community, known=[]):
    seen = set(community + known)
    o_hands = [h for h in all_p_hands if h[0] not in seen and h[1] not in seen]
    print(o_hands, "\n\n")

    o_hands = list(
        sorted(
            o_hands,
            key=cmp_to_key(
                lambda x, y: hand_p_k(x, y, community=community, samples=10)
            ),
            reverse=True,
        )
    )

    return o_hands


def get_hand_rank(hand, community):
    for i, f in enumerate(order):
        final_hand = get_hand(list(hand) + community, f)
        if final_hand:
            return (
                i + (13 - (card_values[final_hand[0][0]] - 1) if i == 8 else 0),
                final_hand,
            )


def compare_hand_k(hand1, hand2):
    for c1, c2 in zip(hand1, hand2):
        v1, v2 = c1[0], c2[0]
        if card_values[v1] > card_values[v2]:
            return 1
        elif card_values[v1] < card_values[v2]:
            return -1

    return 0


def hand_p(*hands, community=[], samples=100):
    seen = set(community + [x for xs in hands for x in xs])
    n_deck = [c for c in deck if c not in seen]
    w_count = [0 for _ in range(len(hands))]
    for r in range(samples):
        new = choices(n_deck, k=5 - len(community))
        winner = get_winner(hands, community + new)
        for w in winner:
            w_count[w[1]] += 1 / len(winner)

    return [w / samples for w in w_count]


def hand_p_k(hand1, hand2, community=[], samples=100):
    return hand_p(hand1, hand2, community=community, samples=samples)[0] - 0.5


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
    p = get_same(cards, 3)
    # TODO Check if needed
    if p == False or len(p) < 3:
        return False
    return p[:3]


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

    cards = sorted(list(set(cards)), key=lambda x: x[0], reverse=True)  # necessary?

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

    for f in order:
        if get_hand(cards, f):
            return get_hand(cards, f)


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

if __name__ == "__main__":
    start = perf_counter()
    # main()
    # print(get_flush(["AC", "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "KD"]))
    # print(get_straight(["AC", "2C", "4C", "5C", "7C", "3D"], True))
    # # print(get_pairs(["AC", "2C", "4C", "5C", "6C", "6D", "8D", "9C", "2D"]))
    # print(get_straight_flush(["AC", "2C", "4C", "5C", "6C", "7C", "8D", "9C", "3C"]))
    # print(get_pair(["AC", "2C", "2S", "6C", "6D", "2D"]))
    # print(get_2pair(["AC", "2C", "2S", "6C", "6D", "2D"]))

    # print(get_winner([("AH", "JC"), ("AS", "3H")], ["AC", "KS", "7C", "JS", "9D"]))
    # print(get_hand_rank(("AH", "JC"), ["AC", "KS", "7C", "JS", "9D"]))
    # print(get_hand_rank(("AH",  "JH"), ["AC", "KH", "7H", "JH", "9D"]))

    # print(get_best_hand(["AC", "2S", "7C", "3S", "9D"]))

    print(all_hands_ranked(["4H", "3C", "3S"]))
    # print(all_hands(["6H", "TD", "2D", "AS", "JH"]))
    # all_hands(["6H", "AD", "AC", "AS", "AH"])

    # print(all_hands([]))

    # print(hand_p(("AH", "JC"), ("AS", "3H"), samples=1_000))
    # print(hand_p_k(("AH", "JC"), ("AS", "3H"), samples=1_000))

    # print(all_hands2(["4D", "3C", "2C"]))
    print(f"Time taken: {(perf_counter() - start) *1000} miliseconds")
