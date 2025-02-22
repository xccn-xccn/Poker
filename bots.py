import random
from misc import strengths, card_values



def pre_flop(hand, player, table):
    pot_odds = (table.pot) / ((table.bets[-1] - player.round_invested) + 3 * table.blinds[-1])
    #not true pot odds adds 3 bb to invested to prevent instant fold from raise

    c1, c2 = hand
    suited = c1[1] == c2[1]

    i1, i2 = sorted(
        (14 - card_values[c1[0]], 14 - card_values[c2[0]]), reverse=not suited
    )

    s = strengths[i1][i2]
    # min_call = 

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
