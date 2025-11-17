def centre(cx: int, cy: int, w: int, h: int) -> tuple[tuple[int, int], tuple[int, int]]:
    return (cx - w // 2, cy - h // 2), (w, h)
