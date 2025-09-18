from build123d import *
from copy import copy
import math
import os


def wood_cube(
    size=40.0,  # mm
    hole_size=29,  # mm
    gap=0.5,  # mm
    split_offset=5,  # mm
    fillet_length=1.0,  # mm
):
    code_name = f"wood-cube-s{size}h{hole_size}o{split_offset}g{gap}f{fillet_length}"

    whole_sketch = Sketch() + Rectangle(size, size)
    whole_sketch_with_circle = whole_sketch - Circle(hole_size / 2.0)
    whole_without_air = extrude(whole_sketch, size)
    whole_with_circle_air = extrude(whole_sketch_with_circle, size)
    whole_with_fillet = fillet(whole_with_circle_air.edges(), fillet_length)

    hole_radius = hole_size / 2.0
    wall_thickness = (size / 2.0 - hole_radius) / 2.0

    fall = gap * ((size / 2.0 - split_offset) / wall_thickness)

    air_up_midline = (
        Location((0, -split_offset, 0))
        * Rotation(X=90)
        * Polyline(
            [
                (-wall_thickness - hole_radius, 0),
                (-wall_thickness - hole_radius - gap, size / 2.0),
                (-wall_thickness - hole_radius, size),
            ]
        )
    )
    air_up_sketch = sweep(air_up_midline, Line((-gap / 2.0, 0.0), (gap / 2.0, 0.0)))
    air_down_sweep = Line(
        (-wall_thickness - hole_radius, -split_offset), (-hole_radius, -size / 2.0)
    )
    air_side = sweep(air_up_sketch, air_down_sweep)
    air_up_outer_edges = air_up_sketch.edges().sort_by(Axis.X)[:2]
    full_air_side = air_side + mirror(air_side, Plane.YZ)

    split_face_half = sweep(air_up_outer_edges, Line((0, 0, 0), (size, 0, 0)))
    split_face_trimmed = split(split_face_half, Plane.YZ, Keep.BOTTOM)
    split_face = split_face_trimmed + mirror(split_face_trimmed, Plane.YZ)

    whole = whole_without_air - full_air_side
    [down_body, up_body] = split(whole, split_face, Keep.BOTH).solids().sort_by(Axis.Y)
    down_body_trim = extrude(Rectangle(size, fall), size)
    down_body_trimmed = (
        down_body - Location((0, -size / 2.0 + fall / 2.0, 0)) * down_body_trim
    )
    down_body_placed = Location((0, -fall, 0)) * down_body_trimmed

    final_up = up_body.intersect(whole_with_fillet)
    final_down = down_body_placed.intersect(whole_with_fillet)

    up_part = Part() + final_up
    up_part.label = "up"
    down_part = Part() + final_down
    down_part.label = "down"
    full = Compound(label="full", children=[up_part, down_part])

    # fillets

    output_directory = f"outputs/{code_name}"
    os.makedirs(output_directory, exist_ok=True)
    export_stl(full, f"{output_directory}/full-{code_name}.stl")
    export_stl(up_part, f"{output_directory}/up-{code_name}.stl")
    export_stl(down_part, f"{output_directory}/down-{code_name}.stl")
    return locals()


def main():
    return wood_cube()


if __name__ == "__main__":
    globals().update(main())
