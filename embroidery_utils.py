"""Shared embroidery helpers that avoid GUI dependencies."""

import math
from typing import List, Tuple


def densify_points(points: List[Tuple[float, float]], max_step_units: float):
    """Ensures stitches are not longer than max_step_units."""
    if len(points) < 2:
        return points[:]

    dense = [points[0]]

    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        dx = x1 - x0
        dy = y1 - y0

        dist = math.hypot(dx, dy)

        if dist <= max_step_units:
            dense.append((x1, y1))
        else:
            steps = int(math.ceil(dist / max_step_units))
            for s in range(1, steps + 1):
                t = s / steps
                xt = x0 + dx * t
                yt = y0 + dy * t
                dense.append((xt, yt))

    return dense


def center_points(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Translate points so their bounding box is centered on the origin."""

    if not points:
        return []

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    center_x = (min(xs) + max(xs)) / 2.0
    center_y = (min(ys) + max(ys)) / 2.0

    return [(x - center_x, y - center_y) for x, y in points]

