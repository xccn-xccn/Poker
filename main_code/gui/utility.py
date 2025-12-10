import random

def centre(cx: int, cy: int, w: int, h: int) -> tuple[tuple[int, int], tuple[int, int]]:
    return (cx - w // 2, cy - h // 2), (w, h)

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

def get_chip_buff():
    l = [0]

    for _ in range(29):
        l.append(l[-1] + random.randint(-1, 1))

    return l
if __name__ == "__main__":
    print(get_chips(20, 149))
