from build123d import *
from copy import copy
import math
import os


def wood_cube(
    size=40.0,  # mm
    hole_size_large=29.0,  # mm
    hole_size_small=27.0,  # mm
    gap=0.2,  # mm
    outer_fillet=2.0,  # mm
    inner_fillet=1.0,  # mm
    magnet_height=3.5,  # mm
    magnet_radius=1.5,  # mm
):
    code_name = f"wood-cube-s{size}h{hole_size_small}-{hole_size_large}g{gap}of{outer_fillet}if{inner_fillet}m{magnet_radius}x{magnet_height}"
    wall_thickness = outer_fillet * 2.0  # mm
    magnet_angle_degrees = 60.0  # degrees
    magnet_angle_radians = math.radians(magnet_angle_degrees)  # degrees
    magnet_gap = 0.2  # mm
    magnet_hole_radius = magnet_radius + magnet_gap  # mm
    magnet_hole_height = magnet_height + magnet_gap  # mm

    half_size = size / 2.0

    whole_sketch = Sketch() + Rectangle(size, size)
    whole_without_air = extrude(whole_sketch, size)
    whole_without_air = fillet(whole_without_air.edges(), outer_fillet)
    edge_snapshots = whole_without_air.edges()
    air = Location((0, 0, size / 4.0)) * Cylinder(
        hole_size_large / 2.0, half_size
    ) + Location((0, 0, size * 3.0 / 4.0)) * Cone(
        hole_size_large / 2.0, hole_size_small / 2.0, half_size
    )
    whole_with_air = whole_without_air - air
    whole_with_fillet = fillet(whole_with_air.edges() - edge_snapshots, inner_fillet)
    whole_with_fillet = fillet(whole_with_air.edges() - edge_snapshots, inner_fillet)

    cut_sketch = Sketch()
    cut_sketch += SlotArc(
        Polyline(
            [
                (-half_size + wall_thickness, -half_size),
                (
                    -half_size
                    + wall_thickness
                    + half_size / math.tan(magnet_angle_radians),
                    0,
                ),
            ]
        ),
        gap,
    )
    cut_air = extrude(cut_sketch, size)
    first_cut_plane = Plane(cut_air.faces().sort_by(Axis.X)[1])
    cut_air += mirror(cut_air, Plane.YZ)

    separated = whole_with_fillet - cut_air
    real_air = whole_with_fillet - separated
    cut_faces = real_air.faces().filter_by(first_cut_plane)

    # two middle faces
    magnet_mount_locations = [
        Plane(face) * grid_loc
        for face in cut_faces
        for grid_loc in GridLocations(0, size - wall_thickness * 2.0, 1, 2)
    ]
    magnet_hole = Location((0, 0, magnet_hole_height / 2.0)) * Cylinder(
        magnet_hole_radius, magnet_hole_height
    )
    magnet = Location((0, 0, magnet_height / 2.0)) * Cylinder(
        magnet_radius, magnet_height
    )
    magnet_holes = [loc * magnet_hole for loc in magnet_mount_locations]
    magnet_holes += [mirror(hole, Plane.YZ) for hole in magnet_holes]

    final_body = separated - magnet_holes
    [up_body, down_body] = final_body.solids().sort_by(Axis.Y)
    up_part = Part() + up_body
    up_part.label = "up"
    down_part = Part() + down_body
    down_part.label = "down"

    magnet_part = Part() + magnet
    magnets = [loc * magnet_part for loc in magnet_mount_locations]
    magnets += [mirror(magnet, Plane.YZ) for magnet in magnets]
    for i, magnet in enumerate(magnets):
        magnet.label = f"magnet{i}"

    full = Compound(label="full", children=[up_part, down_part] + magnets)

    output_directory = f"outputs/{code_name}"
    os.makedirs(output_directory, exist_ok=True)
    export_stl(full, f"{output_directory}/full-{code_name}.stl")
    export_stl(up_part, f"{output_directory}/up-{code_name}.stl")
    export_stl(down_part, f"{output_directory}/down-{code_name}.stl")
    return locals()


def main():
    wood_cube(
        size=40,
        hole_size_large=29,
        hole_size_small=27,
        magnet_height=3.5,
        magnet_radius=1.5,
    )
    wood_cube(
        size=30,
        hole_size_large=23,
        hole_size_small=20,
        magnet_height=2.0,
        magnet_radius=1,
    )


if __name__ == "__main__":
    main()
