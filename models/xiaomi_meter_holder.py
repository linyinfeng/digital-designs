# %% [markdown]
# Exhaust Vent Holder

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

accuracy = 0.2

pole_diameter = 8.08
hook_radius = pole_diameter / 2 + accuracy
hook_width = 10.0
hook_thickness = 2.0

tape_diameter = 24.0

monitor_length = 53.23
monitor_thickness = 13.0
monitor_height = 45.35

hook_height = hook_radius + pole_diameter + monitor_height / 2 + 5.0

with BuildPart() as holder_builder:
    slot_arc_radius = hook_radius + hook_thickness / 2
    with BuildSketch(Plane.YZ):
        SlotArc(CenterArc((0, -slot_arc_radius), slot_arc_radius, 90, 225), hook_thickness)
    extrude(amount=hook_width / 2, both=True)
    with BuildSketch(Plane.XY):
        Rectangle(hook_width, hook_thickness)
    extrude(amount=-hook_height)
    with Locations(Pos(Z=-hook_height) * Rotation(X=90)):
        Cylinder(tape_diameter / 2, hook_thickness)


show(holder_builder, reset_camera=Camera.KEEP)

# %%

from pathlib import Path

script_directory = Path(__file__).resolve().parent
export_stl(holder_builder.part, f"{script_directory}/../outputs/xiaomi_meter_holder.stl")
