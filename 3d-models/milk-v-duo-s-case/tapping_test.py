# %% [markdown]
# Tapping Test

# %%

from decimal import Decimal
import typing
from build123d import *
from ocp_vscode import *
import math
import os
import sys

from pint import UnitRegistry

ureg = UnitRegistry()
f = float

# %%

def show_list(lst, locals, camera=Camera.KEEP):
    lst = lst[:]
    if "test" in locals:
        lst.append(locals["test"])
    show(*lst, reset_camera=camera)

# %%

accuracy = Decimal("0.2")
target_screw_diameter = Decimal("2.5")
standard_hole_diameter = Decimal("2.05")

target_screw_radius = target_screw_diameter / 2
standard_hole_radius = standard_hole_diameter / 2

min_radius = standard_hole_radius - accuracy
max_radius = target_screw_radius + accuracy

min_diameter = min_radius * 2
max_diameter = max_radius * 2

step = Decimal("0.05")

e_to_d = Decimal("1.5")

thickness = Decimal("10")
text_depth = Decimal("1")
text_edge_space = Decimal("1")

class Cell(BasePartObject):
    def __init__(
        self,
        hole_radius: Decimal,
        cell_size: Decimal,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as cell:
            Box(cell_size, cell_size, thickness)
            Cylinder(hole_radius, thickness, mode=Mode.SUBTRACT)
            with BuildPart(Pos((0, -cell_size / 2, thickness / 2)) * Rotation(Z=90)):
                with BuildSketch():
                    text = Text(f"Ø{hole_radius * 2:.2f}", font_size=3, align=(Align.MAX, Align.CENTER))
                Box(text.bounding_box().size.X + f(text_edge_space), cell_size, text_depth * 2, align=(Align.MAX, Align.CENTER, Align.MAX))
                Box(text.bounding_box().size.X, text.bounding_box().size.Y, text_depth, align=(Align.MAX, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
                add(extrude(amount=-text_depth, mode=Mode.PRIVATE))
        super().__init__(cell.part, rotation=rotation, align=align, mode=mode)

class Bar(BasePartObject):
    def __init__(
        self,
        start_diameter: Decimal,
        to_diameter: Decimal,
        step: Decimal = step,
        e_to_d: Decimal = e_to_d,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = None,
        mode: Mode = Mode.ADD,
    ):
        assert to_diameter > start_diameter, "to_diameter must be greater than start_diameter"
        assert ((to_diameter - start_diameter) / step).as_integer_ratio()[1] == 1, "step must divide evenly into the range from start_diameter to to_diameter"

        max_diameter = to_diameter
        cell_size = e_to_d * max_diameter * 2

        with BuildPart() as bar:
            current_diameter = start_diameter
            position = 0
            while current_diameter <= to_diameter:
                x = position * cell_size
                print(f"build Ø{current_diameter} at x {x}")
                with Locations((f(x), 0, 0)):
                    Cell(hole_radius=f(current_diameter / 2), cell_size=cell_size)
                position += 1
                current_diameter += step
        super().__init__(bar.part, rotation=rotation, align=align, mode=mode)

with BuildPart() as tester_builder:
    Bar(min_diameter, max_diameter)

show(tester_builder, reset_camera=Camera.KEEP)

# %%

from pathlib import Path

script_directory = Path(__file__).resolve().parent
export_stl(tester_builder.part, f"{script_directory}/../outputs/tapping_test.stl")
