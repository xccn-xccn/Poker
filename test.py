from winner import *

# with open("hands.txt") as f:
#     data = f.read().splitlines()

from collections import Counter
hands = (line.split() for line in open('hands.txt'))

values = {r:i for i,r in enumerate('23456789TJQKA', 2)}
straights = [(v, v-1, v-2, v-3, v-4) for v in range(14, 5, -1)] + [(14, 5, 4, 3, 2)]
ranks = [(1,1,1,1,1),(2,1,1,1),(2,2,1),(3,1,1),(),(),(3,2),(4,1)]

def hand_rank(hand):
	score = list(zip(*sorted(((v, values[k]) for k,v in Counter(x[0] for x in hand).items()), reverse=True)))
	score[0] = ranks.index(score[0])
	if len(set(card[1] for card in hand)) == 1: score[0] = 5  # flush
	if score[1] in straights: score[0] = 8 if score[0] == 5 else 4  # str./str. flush
	return score



def get_winner1(h1, h2):  
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

    cards = [h1, h2]
    best = []
    for f in order:
        for i, player in enumerate(cards):
            finalHand = get_hand(player, f)

            if finalHand:
                if not best:
                    best = [finalHand, i + 1]
                else:
                    best_player = compare_hand(finalHand, best[0])
                    if best_player == 1:
                        best = [finalHand, i + 1]
                    if best_player == 3:
                        pass  # TODO draws

        if best:
            break

    return best

count = 0
for hand in hands:
    h1 = hand[:5]
    h2 = hand[5:]

    
    if get_winner1(h1, h2)[1] == 1:
        count += 1

print(count)