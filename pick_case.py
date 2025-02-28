from build123d import *
import math
from ocp_vscode import show

slots_number = 15
precision = 0.2  # mm
thickness = 2  # mm
friction_part_thickness = 2  # mm
friction_margin = 0.4  # mm
corner_radius = 3  # mm
fillet_radius = 3  # mm
buckle_length = 5  # mm
buckle_height = 3  # mm
buckle_depth = 1  # mm
buckle_fillet = 0.2  # mm
buckle_angle = 45  # degree
buckle_edge_distance = 3  # mm
front_back_reserve_space = 0.0  # mm
outer_extra_thickness = buckle_depth  # mm
outer_thickness = thickness + friction_part_thickness + outer_extra_thickness  # mm
friction_space = friction_part_thickness + friction_margin  # mm
friction_chamfer_depth = (
    outer_thickness - friction_space - thickness
) * 2.0  # atan(1 / 2) angle
front_back_thickness = outer_thickness + front_back_reserve_space  # mm
pick_thickness = 2.0  # mm
slot_padding = precision  # mm
single_slot_space = pick_thickness + slot_padding * 2
slot_corner_radius = (single_slot_space - precision) / 2.0
slot_spacing = single_slot_space + thickness
total_slots_length = slots_number * single_slot_space + (slots_number - 1) * thickness
pick_width = 35.0  # mm
pick_depth = 35.0  # mm
total_length = total_slots_length + front_back_thickness * 2
total_width = pick_width + outer_thickness * 2
lower_ratio = 0.6
upper_ratio = 1 - lower_ratio
lower_depth = pick_depth * lower_ratio + outer_thickness
friction_depth = lower_depth * 0.6  # mm
upper_depth = pick_depth * upper_ratio + outer_thickness


body = Part()
body_face = Rectangle(total_length, total_width)
body_main = extrude(body_face, amount=lower_depth)
body += body_main
end_face_center = body.faces().sort_by(Axis.X).first.center()
remove_sketch_plane = Plane(
    origin=end_face_center + (front_back_thickness, 0, 0),
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0),
)
body_top_face = body.faces().sort_by(Axis.Z).last

# slots air
air = Part()
air_curve = Spline(
    [
        (total_width / 2.0 - outer_thickness, lower_depth / 2.0),
        (0, -(lower_depth / 2.0 - outer_thickness)),
        (-(total_width / 2.0 - outer_thickness), lower_depth / 2.0),
    ]
)
air_curve_close = Line(air_curve @ 0, air_curve @ 1)
air_face = make_face([air_curve, air_curve_close])
air += extrude(air_face, amount=total_length - front_back_thickness * 2)
keep_air = Part()
pick_slot_face = RectangleRounded(
    single_slot_space, total_width - outer_thickness * 2.0, radius=slot_corner_radius
)
pick_slot_box = extrude(pick_slot_face, amount=lower_depth)
for slot_index in range(slots_number):
    slot_bottom_z = slot_index * slot_spacing
    slot_center_z = slot_bottom_z + single_slot_space / 2.0
    keep_air += (
        Pos(0.0, -lower_depth / 2.0, slot_center_z)
        * Rotation(Z=90)
        * Rotation(Y=90)
        * pick_slot_box
    )
air &= keep_air


# friction part
def make_friction_style_part(thickness):
    part = Part()
    rect = Rectangle(total_length - thickness * 2, total_width - thickness * 2)
    face = Rectangle(total_length, total_width) - rect
    part += extrude(face, amount=-friction_depth)
    return part


friction_part = make_friction_style_part(friction_part_thickness)

# friction air
friction_air = make_friction_style_part(friction_space)

# buckle
buckle = Part()
buckle_sketch = Rectangle(buckle_length, buckle_height)
buckle += extrude(buckle_sketch, amount=buckle_depth, taper=buckle_angle)
buckle = fillet(
    buckle.edges()
    - buckle.edges().filter_by(Axis.X)
    - buckle.edges().filter_by(Axis.Y),
    radius=buckle_fillet,
)
buckle = fillet(buckle.edges().group_by(Axis.Z)[-1], radius=buckle_fillet)

# finish body
removed_friction_air = Plane(body_top_face) * friction_air
body -= removed_friction_air
body = fillet(body.edges().filter_by(Axis.Z), radius=fillet_radius)
body = fillet(body.edges().group_by(Axis.Z)[0], radius=fillet_radius)
body = chamfer(
    body.edges().group_by(Axis.Z)[-1],
    length2=outer_thickness - friction_space - thickness,
    length=friction_chamfer_depth,
)
body -= remove_sketch_plane * air
buckle_front_air_plane = Plane(
    removed_friction_air.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
)  # front inner
front_buckle_air = (
    buckle_front_air_plane * Pos(Y=friction_depth / 2.0 - buckle_edge_distance) * buckle
)
body -= front_buckle_air
body -= front_buckle_air.mirror(Plane.XZ)

# upper case
upper_case = Part()
upper_box = extrude(body_face, amount=upper_depth)
upper_box_air = extrude(
    Rectangle(
        total_length - friction_part_thickness * 2,
        total_width - friction_part_thickness * 2,
    ),
    amount=upper_depth - outer_thickness,
    taper=math.degrees(
        math.atan(
            (outer_thickness - friction_part_thickness)
            / (upper_depth - outer_thickness)
        )
    ),
)
upper_case = upper_box - upper_box_air
upper_case += friction_part
upper_case = fillet(upper_case.edges().filter_by(Axis.Z), radius=fillet_radius)
upper_case = fillet(upper_case.edges().group_by(Axis.Z)[-1], radius=fillet_radius)
buckle_front_mount_plane = Plane(
    friction_part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
)  # front inner
front_buckle = (
    buckle_front_mount_plane
    * Pos(Y=friction_depth / 2.0 - buckle_edge_distance)
    * buckle
)
upper_case += front_buckle
upper_case += front_buckle.mirror(Plane.XZ)

body.label = "body"
upper_case.label = "case"
assembly = Compound(label="assembly", children=[body, Pos(Z=lower_depth) * upper_case])

show(assembly)
export_stl(body, "outputs/body.stl")
export_stl(Rotation(X=180) * upper_case, "outputs/case.stl")
