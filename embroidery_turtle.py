# embroidery_turtle.py

import turtle
import math
import os
from pyembroidery import EmbPattern, write_pes, write_png
<<<<<<< ours
from embroidery_utils import center_points, center_stitches, densify_points
=======
from embroidery_utils import center_points, densify_points
>>>>>>> theirs


class EmbroideryTurtle(turtle.Turtle):
    """
    A Turtle that records stitch points only when the pen is DOWN.
    Coordinates are in 'turtle units'. A scale factor will convert
    them to millimetres during export.
    """
    def __init__(self):
        super().__init__()
        self.record = False
        self.stitch_points = []

    def _record_point(self):
        if self.record:
            x, y = self.position()
            self.stitch_points.append((x, y))

    def pendown(self):
        super().pendown()
        self.record = True
        self._record_point()

    def penup(self):
        super().penup()
        self.record = False

    def goto(self, x, y=None):
        if y is None:
            x, y = x
        super().goto(x, y)
        self._record_point()

    def forward(self, distance):
        super().forward(distance)
        self._record_point()

    def backward(self, distance):
        super().backward(distance)
        self._record_point()


def export_to_embroidery(
    t: EmbroideryTurtle,
    scale_mm=1.0,                # <--- NEW scaling factor
    max_stitch_mm=3.0,
    pes_filename="design.pes",
    png_filename="design.png",
    show_preview=True,
):
    """Convert turtle units → mm using scale_mm."""

    points = center_points(t.stitch_points)

    if len(points) < 2:
        print("Not enough points to make stitches.")
        return

    centered_points = center_points(points)

    # Convert max stitch length (mm) → turtle units
    max_step_units = max_stitch_mm / scale_mm

    dense_points = densify_points(centered_points, max_step_units=max_step_units)

    stitches = []
    for x, y in dense_points:
        ex = int(x * scale_mm)
        ey = int(-y * scale_mm)  # invert y
        stitches.append((ex, ey))

    centered_stitches = center_stitches(stitches)

    pattern = EmbPattern()
    pattern.add_block(centered_stitches)
    pattern.move_center_to_origin()

    write_pes(pattern, pes_filename)
    write_png(pattern, png_filename)

    print(f"Saved PES : {os.path.abspath(pes_filename)}")
    print(f"Saved PNG : {os.path.abspath(png_filename)}")
    print(f"Stitches  : {len(centered_stitches)}")

    if show_preview:
        try:
            from PIL import Image
            Image.open(png_filename).show()
        except:
            pass
