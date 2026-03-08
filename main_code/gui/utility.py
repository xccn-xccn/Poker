import random


def centre(
    centre_x: int, centre_y: int, w: int, h: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (centre_x - w // 2, centre_y - h // 2), (w, h)


def get_chips(bb: int, bet: int):
    chip_values = {
        max(bb // 20, 1): "white",
        max(bb // 2, 1): "red",
        max(bb, 1): "orange",
        max(int(2.5 * bb), 1): "green",
        max(5 * bb, 1): "blue",
        max(25 * bb, 1): "black",
        max(50 * bb, 1): "purple",
        max(500 * bb, 1): "brown",
    }

    chips = []
    remaining = bet

    # print(bb, list(chip_values.items()))
    for value, name in sorted(
        list(chip_values.items()), key=lambda x: x[0], reverse=True
    ):
        # print(remaining, value, remaining // value)
        chips += [name] * int(remaining // value)
        remaining = remaining % value

    return chips


def get_chip_buff():
    l = [0]

    for _ in range(29):
        l.append(l[-1] + random.randint(-1, 1))

    return l


if __name__ == "__main__":
    print(get_chips(20, 149))
