from build123d import *
import math
import ocp_vscode as ov
from ocp_vscode import show

def slot_face(width, space):
    pick_slot_face = Rectangle(
        space, width - space,
    )
    pick_slot_end_circle = Circle(radius=space / 2.0)
    pick_slot_face += Pos(pick_slot_face.edges().sort_by(Axis.Y)[0].center()) * pick_slot_end_circle
    pick_slot_face += Pos(pick_slot_face.edges().sort_by(Axis.Y)[-1].center()) * pick_slot_end_circle
    return pick_slot_face

def rectangle_donut_outer_edges(edges, origin=(0, 0, 0)):
    return (
        edges.filter_by(Axis.X).sort_by_distance(origin)[-2:]
        + edges.filter_by(Axis.Y).sort_by_distance(origin)[-2:]
    )


def guitar_pick_case(
    # manufacturing
    precision=0.2,  # mm
    # pick
    pick_thickness=2.0,  # mm
    pick_width=35.0,  # mm
    pick_depth=35.0,  # mm
    # slot
    slots_number=15,  # mm
    # slot
    wall_thickness=2,  # mm
    slot_padding=None,  # mm, default = precision
    slot_extend=0.5,  # mm
    slot_extend_depth=2,  # mm
    # body
    lower_ratio=0.6,
    body_fillet_radius=3,  # mm
    # body and case
    anti_pinch_fillet_radius=1,  # mm
    # friction part
    friction_part_thickness=1.2,  # mm
    friction_gap=0.2,  # mm
    front_back_reserve_space=0.0,  # mm
    left_right_reserve_space=0.0,  # mm
    # buckle
    buckle_length=5,  # mm
    buckle_height=3,  # mm
    buckle_depth=0.5,  # mm
    buckle_fillet=0.2,  # mm
    buckle_angle=45,  # degree
    buckle_edge_distance=3,  # mm
):
    if not slot_padding:
        slot_padding = precision

    outer_extra_thickness = buckle_depth  # mm
    outer_thickness = (
        wall_thickness + friction_part_thickness + outer_extra_thickness
    )  # mm
    friction_space_on_body = friction_part_thickness + friction_gap  # mm
    friction_chamfer_depth = (
        outer_thickness - friction_space_on_body - wall_thickness
    ) * 2.0  # atan(1 / 2) angle
    front_back_thickness = outer_thickness + front_back_reserve_space  # mm
    left_right_thickness = outer_thickness + left_right_reserve_space  # mm
    single_slot_space = pick_thickness + slot_padding * 2
    single_slot_space_extended = single_slot_space + slot_extend * 2
    slot_spacing = single_slot_space + wall_thickness
    total_slots_length = (
        slots_number * single_slot_space + (slots_number - 1) * wall_thickness
    )
    slot_width = pick_width
    total_length = total_slots_length + front_back_thickness * 2
    total_width = slot_width + left_right_thickness * 2
    upper_ratio = 1 - lower_ratio
    lower_depth = pick_depth * lower_ratio + outer_thickness
    slot_depth = lower_depth - wall_thickness
    friction_depth = buckle_edge_distance * 2 + friction_chamfer_depth
    upper_depth = pick_depth * upper_ratio + wall_thickness

    assert buckle_edge_distance * 2 > buckle_height, "incomplete buckle"
    assert lower_ratio > 0.5, "prevent pick fall off"

    body = Part()
    body_face = Rectangle(total_length, total_width)
    body_main = extrude(body_face, amount=lower_depth)
    body += body_main
    remove_slot_air_face = body.faces().sort_by(Axis.X).first
    remove_slot_air_plane = Plane(remove_slot_air_face).rotated((0, 180, 0))
    body_top_face = body.faces().sort_by(Axis.Z).last

    # slots air
    slot_air = Part()
    air_sketch = Sketch()
    slot_bottom_y = lower_depth / 2.0 - slot_depth
    air_curve = Spline(
        [
            (slot_width / 2.0, lower_depth / 2.0),
            (0, slot_bottom_y),
            (-(slot_width / 2.0), lower_depth / 2.0),
        ],
    )
    air_sketch += make_face(air_curve.close())
    slot_air += extrude(air_sketch, amount=total_length)
    keep_slot_air = Part()
    pick_slot_face = slot_face(slot_width, single_slot_space)
    sweep_curve = split(air_curve, bisect_by=Plane.YZ)
    pick_slot_main = sweep((sweep_curve ^ 0) * Rotation(Z=-90) * Pos(Y=slot_width / 2.0) * split(pick_slot_face, bisect_by=Plane.XZ),
                               sweep_curve,
                               is_frenet=True)
    pick_slot_main += pick_slot_main.mirror(Plane.YZ)
    pick_slot_main = Pos(Y=-lower_depth / 2.0 + slot_extend_depth) * pick_slot_main
    pick_slot_main = split(pick_slot_main, Plane.XZ)
    pick_slot_main = Rotation(Z=90) * Rotation(X=-90) * pick_slot_main
    pick_slot_entry_sketch = Sketch()
    pick_slot_extended_face = RectangleRounded(
        single_slot_space_extended,
        slot_width,
        radius=single_slot_space / 2.0,
    )
    pick_slot_entry_sketch += pick_slot_extended_face
    pick_slot_entry_sketch += Pos(Z=slot_extend_depth) * pick_slot_main.faces().sort_by(Axis.Z)[0]
    pick_slot_entry = loft(pick_slot_entry_sketch)
    pick_slot_box = pick_slot_entry + Pos(Z=slot_extend_depth) * pick_slot_main
    slot_center_z = front_back_thickness + single_slot_space / 2.0
    for slot_index in range(slots_number):
        keep_slot_air += (
            Pos(0.0, lower_depth / 2.0, slot_center_z)
            * Rotation(Z=270)
            * Rotation(Y=90)
            * pick_slot_box
        )
        slot_center_z += slot_spacing
    slot_air &= keep_slot_air

    # friction part
    def make_friction_style_part(thickness):
        part = Part()
        rect = Rectangle(total_length - thickness * 2, total_width - thickness * 2)
        face = Rectangle(total_length, total_width) - rect
        part += extrude(face, amount=-friction_depth)
        return part

    # friction air
    friction_air = make_friction_style_part(friction_space_on_body)

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
    body = fillet(body.edges().filter_by(Axis.Z), radius=body_fillet_radius)
    body = fillet(body.edges().group_by(Axis.Z)[0], radius=body_fillet_radius)
    middle_edges = body.edges().filter_by(Plane.XY).group_by(Axis.Z)[-2]
    middle_outer_edges = rectangle_donut_outer_edges(middle_edges)
    # return locals()
    body = fillet(middle_outer_edges, radius=anti_pinch_fillet_radius)
    body = chamfer(
        body.edges().group_by(Axis.Z)[-1],
        length2=outer_thickness - friction_space_on_body - wall_thickness,
        length=friction_chamfer_depth,
    )
    remove_slot_air = remove_slot_air_plane * slot_air
    body -= remove_slot_air
    buckle_front_air_plane = Plane(
        removed_friction_air.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
    )  # front inner
    front_buckle_air = (
        buckle_front_air_plane
        * Pos(Y=friction_depth / 2.0 - buckle_edge_distance)
        * buckle
    )
    body -= front_buckle_air
    body -= front_buckle_air.mirror(Plane.XZ)

    # upper case
    upper_case = Part()
    upper_case = extrude(body_face, amount=upper_depth)
    friction_part = make_friction_style_part(friction_part_thickness)
    upper_case += friction_part
    upper_case = fillet(upper_case.edges().filter_by(Axis.Z), radius=body_fillet_radius)
    upper_case = fillet(
        upper_case.edges().group_by(Axis.Z)[-1], radius=body_fillet_radius
    )
    upper_case = fillet(
        rectangle_donut_outer_edges(upper_case.edges().group_by(Axis.Z)[0]),
        radius=anti_pinch_fillet_radius,
    )
    upper_box_air = extrude(
        Rectangle(
            total_length - friction_part_thickness * 2,
            total_width - friction_part_thickness * 2,
        ),
        amount=upper_depth - wall_thickness,
        taper=math.degrees(
            math.atan(
                (outer_thickness - friction_part_thickness)
                / (upper_depth - outer_thickness)
            )
        ),
    )
    upper_box_air = fillet(upper_box_air.edges().group_by(Axis.Z)[-2], radius=body_fillet_radius)
    upper_box_air = fillet(upper_box_air.edges().group_by(Axis.Z)[-1], radius=body_fillet_radius)
    upper_case = upper_case - upper_box_air

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
    assembly = Compound(
        label="assembly", children=[body, Pos(Z=lower_depth) * upper_case]
    )
    packed = pack([body, Rotation(X=180) * upper_case], padding=5, align_z=True)

    ov.show_all()

    print()
    total_volume = sum(part.volume for part in assembly.solids())
    print(f"volume: {total_volume} mm^3")

    export_stl(body, "outputs/body.stl")
    export_stl(Rotation(X=180) * upper_case, "outputs/case.stl")
    export_stl(assembly, "outputs/assembly.stl")
    export_stl(Compound(packed), "outputs/pack.stl")

    export_step(body, "outputs/body.step")
    export_step(Rotation(X=180) * upper_case, "outputs/case.step")
    export_step(assembly, "outputs/assembly.step")
    return locals()


def main():
    return guitar_pick_case()


if __name__ == "__main__":
    globals().update(main())
