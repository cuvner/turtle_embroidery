# api_backend.py

"""Headless embroidery helpers for the web API.

This file turns a small set of turtle-like commands into stitched points and
returns PES/PNG bytes for download.
"""

import base64
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
import ast
from typing import Dict, Iterable, List, Tuple

<<<<<<< ours
from embroidery_utils import center_points_with_offset, center_stitches, densify_points
=======
from embroidery_utils import center_points, densify_points
>>>>>>> theirs
from pyembroidery import EmbPattern, write_pes, write_png


@dataclass
class Command:
    op: str
    value: float = 0.0
    x: float = 0.0
    y: float = 0.0


class VirtualEmbroidery:
    """Minimal turtle-like state tracker without a GUI."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0  # degrees, 0 = east
        self.pen_down = False
        self.points: List[Tuple[float, float]] = []

    def _record(self):
        if self.pen_down:
            self.points.append((self.x, self.y))

    def penup(self):
        self.pen_down = False

    def pendown(self):
        self.pen_down = True
        self._record()

    def goto(self, x: float, y: float):
        self.x = x
        self.y = y
        self._record()

    def forward(self, distance: float):
        radians = math.radians(self.heading)
        self.x += math.cos(radians) * distance
        self.y += math.sin(radians) * distance
        self._record()

    def backward(self, distance: float):
        self.forward(-distance)

    def right(self, angle: float):
        self.heading -= angle

    def left(self, angle: float):
        self.heading += angle


SUPPORTED_OPS = {
    "penup",
    "pendown",
    "goto",
    "forward",
    "backward",
    "right",
    "left",
}


def _num(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    raise ValueError("expected a number literal")


def _call_to_command(call: ast.Call) -> Dict:
    if not isinstance(call.func, ast.Name):
        raise ValueError("unsupported call")
    name = call.func.id.lower()
    if name not in SUPPORTED_OPS:
        raise ValueError(f"unsupported op: {name}")

    if name in {"penup", "pendown"}:
        if call.args:
            raise ValueError(f"{name} takes no arguments")
        return {"op": name}

    if name in {"forward", "backward", "left", "right"}:
        if len(call.args) != 1:
            raise ValueError(f"{name} takes one argument")
        return {"op": name, "value": _num(call.args[0])}

    if name == "goto":
        if len(call.args) != 2:
            raise ValueError("goto takes two arguments")
        return {"op": name, "x": _num(call.args[0]), "y": _num(call.args[1])}

    raise ValueError(f"unsupported op: {name}")


def _walk(node: ast.AST) -> List[Dict]:
    cmds: List[Dict] = []

    if isinstance(node, ast.Expr):
        if not isinstance(node.value, ast.Call):
            raise ValueError("only function calls are allowed")
        cmds.append(_call_to_command(node.value))
        return cmds

    if isinstance(node, ast.For):
        if not isinstance(node.iter, ast.Call) or not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
            raise ValueError("for loops must be 'for _ in range(n):'")
        if len(node.iter.args) != 1:
            raise ValueError("range must have one argument")
        count = int(_num(node.iter.args[0]))
        if count < 0 or count > 10000:
            raise ValueError("range must be between 0 and 10000")
        body_cmds: List[Dict] = []
        for child in node.body:
            body_cmds.extend(_walk(child))
        for _ in range(count):
            cmds.extend(body_cmds)
        return cmds

    raise ValueError("only simple calls and for-range loops are allowed")


def script_to_commands(script: str) -> List[Dict]:
    """Parse a tiny turtle DSL (Python subset) into commands."""
    try:
        tree = ast.parse(script)
    except SyntaxError as exc:
        raise ValueError(f"syntax error: {exc.msg}") from exc

    commands: List[Dict] = []
    for node in tree.body:
        commands.extend(_walk(node))
    return commands


def run_commands(commands: Iterable[Dict]) -> List[Tuple[float, float]]:
    """Run a list of dict commands and return recorded points."""

    vt = VirtualEmbroidery()

    for raw in commands:
        if "op" not in raw:
            raise ValueError("Command missing 'op'")

        op = raw["op"].lower()
        if op not in SUPPORTED_OPS:
            raise ValueError(f"Unsupported op: {op}")

        value = float(raw.get("value", 0.0))

        if op == "penup":
            vt.penup()
        elif op == "pendown":
            vt.pendown()
        elif op == "goto":
            try:
                x = float(raw["x"])
                y = float(raw["y"])
            except KeyError as exc:
                raise ValueError("goto requires x and y") from exc
            vt.goto(x, y)
        elif op == "forward":
            vt.forward(value)
        elif op == "backward":
            vt.backward(value)
        elif op == "right":
            vt.right(value)
        elif op == "left":
            vt.left(value)

    return vt.points


def points_to_outputs(
    points: List[Tuple[float, float]],
    scale_mm: float,
    max_stitch_mm: float,
) -> Dict[str, object]:
    """Convert points to PES/PNG bytes and stitch metadata."""

    centered_points, center_offset = center_points_with_offset(points)

    if len(centered_points) < 2:
        raise ValueError("At least two points are required to make stitches")

    centered_points = center_points(points)

    max_step_units = max_stitch_mm / scale_mm
    dense_points = densify_points(centered_points, max_step_units=max_step_units)

    stitches = []
    for x, y in dense_points:
        ex = int(x * scale_mm)
        ey = int(-y * scale_mm)
        stitches.append((ex, ey))

    centered_stitches = center_stitches(stitches)

    pattern = EmbPattern()
    pattern.add_block(centered_stitches)
    pattern.move_center_to_origin()

    with tempfile.TemporaryDirectory() as tmpdir:
        pes_path = os.path.join(tmpdir, "design.pes")
        png_path = os.path.join(tmpdir, "design.png")

        write_pes(pattern, pes_path)
        write_png(pattern, png_path)

        pes_bytes = Path(pes_path).read_bytes()
        png_bytes = Path(png_path).read_bytes()

    return {
        "pes_base64": base64.b64encode(pes_bytes).decode("ascii"),
        "png_base64": base64.b64encode(png_bytes).decode("ascii"),
        "stitch_count": len(centered_stitches),
        "center_offset": {"x": center_offset[0], "y": center_offset[1]},
        "centered_points": [[x, y] for x, y in centered_points],
    }


def generate_from_commands(
    commands: Iterable[Dict],
    scale_mm: float,
    max_stitch_mm: float,
) -> Dict[str, object]:
    points = run_commands(commands)
    return points_to_outputs(points, scale_mm=scale_mm, max_stitch_mm=max_stitch_mm)
