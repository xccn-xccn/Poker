from collections import Counter

cardValues = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
    1: "A",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "T",
    11: "J",
    12: "Q",
    13: "K",
    14: "A",
}


def get_winner(hands, community):#TODO finish - consider to loop the order or each hand
    order = [
        get_straight_flush,
        get_four,
        get_house,
        get_flush,
        get_straight,
        get_three,
        get_2pair,
        get_pair
    ]


def get_hand(cards):
    pass


def get_same(cards, n):
    c_cards = Counter([c[0] for c in cards])

    pairs = []
    for card, val in c_cards.items():
        if val >= n:
            pairs.append(card)

    output = sorted(
        [c for c in cards if c[0] in pairs],
        key=lambda x: cardValues[x[0]],
        reverse=True,
    )

    return output if output else False


def get_pair(cards):
    p = get_same(cards, 2)
    return p[:2] if p else False


def get_2pair(cards):
    p = get_same(cards, 2)
    if len(p) < 4:
        return False
    return p[:4]


def get_three(cards):
    return get_same(cards, 3)


def get_house(cards):
    three = get_three(cards)
    if not three:
        return False
    remaining = [c for c in cards if c not in three]
    pair = get_pair(remaining)[:2]

    if three and pair:
        return three + pair

    return False


def get_four(cards):
    return get_same(cards, 4)


def get_straight(cards, l_5=True):
    copyCards = cards.copy()
    cards = []
    print(l_5)
    for c in copyCards:
        cards.append((cardValues[c[0]], c[1]))
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
    return False if len(straight) < 5 else [cardValues[v] + s for v, s in straight]


def get_flush(cards, l_5=True):
    cardSuits = [c[1] for c in cards]
    c_cards = Counter(cardSuits)

    most = c_cards.most_common(1)[0]
    if most[1] >= 5:
        suit = most[0]
    else:
        return False

    output = sorted(
        [c for c in cards if c[1] == suit], key=lambda x: cardValues[x[0]], reverse=True
    )
    if l_5:
        output = output[:5]

    return output


def get_straight_flush(cards):
    f_cards = get_flush(cards, l_5=False)

    print(f_cards)
    s_f_cards = get_straight(f_cards)

    return s_f_cards


if __name__ == "__main__":
    print(get_flush(["AC", "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "KD"]))
    # print(get_straight(["AC", "2C", "4C", "5C", "6C", "7C", "8D", "9C", "3D"]))
    # print(get_pairs(["AC", "2C", "4C", "5C", "6C", "6D", "8D", "9C", "2D"]))
    print(get_straight_flush(["AC", "2C", "4C", "5C", "6C", "7C", "8D", "9C", "3C"]))
    print(get_pair(["AC", "2C", "2S", "6C", "6D", "2D"]))
    print(get_2pair(["AC", "2C", "2S", "6C", "6D", "2D"]))
