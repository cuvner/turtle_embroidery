"""Reusable embroidery builder that keeps patterns centered.

The class here mirrors the ad-hoc logic that previously lived across
``api_backend`` and ``embroidery_turtle`` but consolidates it so centering
rules stay consistent everywhere.
"""

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from embroidery_utils import (
    center_points_with_offset,
    center_stitches,
    densify_points,
    finish_pattern,
)
from pyembroidery import EmbPattern, write_pes, write_png


@dataclass
class PyEmbroideryBuilder:
    scale_mm: float
    max_stitch_mm: float
    points: List[Tuple[float, float]] = field(default_factory=list)
    centered_points: List[Tuple[float, float]] = field(default_factory=list)
    center_offset: Tuple[float, float] = (0.0, 0.0)
    stitches: List[Tuple[int, int]] = field(default_factory=list)
    pattern: Optional[EmbPattern] = None

    def _build_stitches(self) -> List[Tuple[int, int]]:
        if len(self.points) < 2:
            raise ValueError("At least two points are required to make stitches")

        self.centered_points, self.center_offset = center_points_with_offset(self.points)

        max_step_units = self.max_stitch_mm / self.scale_mm
        dense_points = densify_points(self.centered_points, max_step_units=max_step_units)

        stitches: List[Tuple[int, int]] = []
        for x, y in dense_points:
            ex = int(round(x * self.scale_mm))
            ey = int(round(-y * self.scale_mm))  # invert y
            stitches.append((ex, ey))

        centered = center_stitches(stitches)
        self.stitches = centered
        return centered

    def build_pattern(self) -> EmbPattern:
        centered_stitches = self._build_stitches()
        pattern = EmbPattern()
        pattern.add_block(centered_stitches)
        self.pattern = finish_pattern(pattern)
        return self.pattern

    def ensure_pattern(self) -> EmbPattern:
        if self.pattern is None:
            return self.build_pattern()
        return self.pattern

    def export_files(self, pes_filename: str, png_filename: str) -> None:
        pattern = self.ensure_pattern()
        write_pes(pattern, pes_filename)
        write_png(pattern, png_filename)

    def export_bytes(self) -> Tuple[bytes, bytes]:
        pattern = self.ensure_pattern()

        with tempfile.TemporaryDirectory() as tmpdir:
            pes_path = os.path.join(tmpdir, "design.pes")
            png_path = os.path.join(tmpdir, "design.png")

            write_pes(pattern, pes_path)
            write_png(pattern, png_path)

            pes_bytes = Path(pes_path).read_bytes()
            png_bytes = Path(png_path).read_bytes()

        return pes_bytes, png_bytes
