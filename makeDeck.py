deck = []
for suit in ("CSHD"):
    for n in ("A23456789TJQK"):
        deck.append(n + suit)

print(deck)