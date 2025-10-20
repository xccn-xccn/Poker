def get_chips(bb, bet):
    chip_values = {
        bb // 20: "white",
        bb // 2: "red",
        bb: "orange",
        int(2.5 * bb): "green",
        5 * bb: "blue",
        25 * bb: "black",
        50 * bb: "purple",
        500 * bb: "brown",
    }
    chips = []
    remaining = bet
    for value, name in sorted(list(chip_values.items()), key= lambda x: x[0], reverse=True):
        chips += [name] * (remaining // value)
        remaining = remaining % value

    return chips

if __name__ == "__main__":
    print(get_chips(20, 149))
