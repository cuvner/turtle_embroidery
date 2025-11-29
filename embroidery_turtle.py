# embroidery_turtle.py

import os
import turtle

from pyembroidery import END, JUMP, EmbPattern, write_pes, write_png

from test_class_pyembr import PyEmbroideryBuilder


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


class TurtleEmbroidery:
    """Helpers for preparing :class:`EmbPattern` objects for export."""

    @staticmethod
    def center_pattern(pattern: EmbPattern) -> EmbPattern:
        pattern.move_center_to_origin()
        return pattern

    @staticmethod
    def remove_trailing_jumps(pattern: EmbPattern) -> EmbPattern:
        """Strip jump commands from the tail of the pattern."""

        while getattr(pattern, "stitches", []):
            command = pattern.stitches[-1][0]
            if command == JUMP:
                pattern.stitches.pop()
            else:
                break

        return pattern

    @staticmethod
    def finish(pattern: EmbPattern) -> EmbPattern:
        """Finalize a pattern by centering, trimming, and appending END."""

        return PyEmbroideryBuilder.finish_pattern(pattern)


def export_pattern(
    pattern: EmbPattern,
    pes_filename: str = "design.pes",
    png_filename: str = "design.png",
    show_preview: bool = True,
):
    """Write a finished pattern to PES/PNG, ensuring it ends cleanly."""

    stitches = getattr(pattern, "stitches", [])
    if not stitches:
        print("No stitches to export.")
        return

    last = pattern.get_stitch(-1) if hasattr(pattern, "get_stitch") else stitches[-1]
    last_command = getattr(last, "command", last[0])
    if last_command != END:
        pattern.add_stitch_absolute(END, 0, 0)

    write_pes(pattern, pes_filename)
    write_png(pattern, png_filename)

    print(f"Saved PES : {os.path.abspath(pes_filename)}")
    print(f"Saved PNG : {os.path.abspath(png_filename)}")
    print(f"Stitches  : {len(pattern.stitches)}")

    if show_preview:
        try:
            from PIL import Image

            Image.open(png_filename).show()
        except Exception:
            pass


def export_to_embroidery(
    t: EmbroideryTurtle,
    scale_mm: float = 1.0,
    max_stitch_mm: float = 3.0,
    pes_filename: str = "design.pes",
    png_filename: str = "design.png",
    show_preview: bool = True,
):
    """Convert turtle units → mm using ``scale_mm`` and export."""

    builder = PyEmbroideryBuilder(scale_mm=scale_mm, max_stitch_mm=max_stitch_mm)
    builder.points = t.stitch_points

    try:
        pattern = builder.build_pattern()
    except ValueError:
        print("Not enough points to make stitches.")
        return

    builder.export_files(pes_filename, png_filename)

    print(f"Saved PES : {os.path.abspath(pes_filename)}")
    print(f"Saved PNG : {os.path.abspath(png_filename)}")
    print(f"Stitches  : {len(pattern.stitches)}")

    if show_preview:
        try:
            from PIL import Image

            Image.open(png_filename).show()
        except Exception:
            pass
