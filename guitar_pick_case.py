from build123d import *
import math
from copy import copy
import ocp_vscode as ov
from ocp_vscode import show
import datetime
import os


def slot_sweep_face(width, space, *, slot_tilt, slot_open):
    pick_slot_face = Sketch()
    tilted_space = space * math.cos(math.radians(slot_tilt))
    rect = Rectangle(
        tilted_space,
        width - tilted_space,
    )
    pick_slot_face += rect
    pick_slot_end_circle = Circle(radius=tilted_space / 2.0)
    end_circle_left = (
        Pos(pick_slot_face.edges().sort_by(Axis.Y)[0].center()) * pick_slot_end_circle
    )
    end_circle_right = (
        Pos(pick_slot_face.edges().sort_by(Axis.Y)[-1].center()) * pick_slot_end_circle
    )
    pick_slot_face += end_circle_left
    pick_slot_face += end_circle_right
    open_at = rect.vertices().group_by(Axis.X)[0]
    arc_sagitta = slot_open * math.cos(math.radians(slot_tilt))
    arc = SagittaArc(open_at.first, open_at.last, arc_sagitta)
    pick_slot_face += make_face(arc.close())
    return pick_slot_face


def rectangle_donut_outer_edges(edges, origin=(0, 0, 0)):
    return (
        edges.filter_by(Axis.X).sort_by_distance(origin)[-2:]
        + edges.filter_by(Axis.Y).sort_by_distance(origin)[-2:]
    )


def guitar_pick_case(
    # output
    auto_code_name=False,
    code_name="prototype",
    # manufacturing
    precision=0.2,  # mm
    # pick
    pick_thickness=2,  # mm
    pick_width=35,  # mm
    pick_depth=35,  # mm
    # slot
    slots_per_row=15,  # mm
    slots_rows=2,
    slot_width_ratio=1.0,  # mm
    slot_row_extra_spacing=5,  # mm
    slot_tilt=30,  # mm
    slot_open=1,  # mm
    # slot
    wall_thickness=2,  # mm
    slot_padding=None,  # mm, default = precision
    slot_open_fillet=0.5,  # mm
    # body
    lower_ratio=0.6,
    body_fillet_radius=3,  # mm
    body_bottom_fillet_radius=3,  # mm
    outer_extra_thickness=None,  # mm, default = buckle_depth or 0
    friction_chamfer=0.5,  # mm
    friction_chamfer_depth=1,  # mm
    # case
    upper_case_top_fillet_radius=3,  # mm
    upper_case_inner_fillet_radius=3,  # mm
    # body and case
    anti_pinch_fillet_radius=1,  # mm
    # friction part
    friction_part_thickness=2,  # mm
    friction_gap=0.2,  # mm
    front_back_reserve_space=0,  # mm
    left_right_reserve_space=0,  # mm
    # magnet
    enable_magnet=True,
    magnet_radius=3.0 / 2.0,  # mm
    magnet_height=3.5,  # mm
    magnet_radius_padding=0.2,  # mm
    magnet_height_padding=0.2,  # mm
    magnet_slot_inner_fillet_radius=0.1,  # mm
    magnet_slot_outer_fillet_radius=0.2,  # mm
    magnet_fillet_radius=0.2,  # mm
    magnet_y_count=3,
    # buckle
    enable_buckle=True,
    buckle_length=5,  # mm
    buckle_height=3,  # mm
    buckle_depth=0.5,  # mm
    buckle_fillet=0.2,  # mm
    buckle_angle=45,  # degree
    buckle_edge_distance=2,  # mm
    # water mark
    enable_watermark=False,
):
    if auto_code_name:
        code_name = f"{slots_rows}x{slots_per_row}-w{pick_width}d{pick_width}t{pick_thickness}-t{slot_tilt}"

    if not slot_padding:
        slot_padding = precision

    if not outer_extra_thickness:
        if enable_buckle:
            outer_extra_thickness = buckle_depth  # mm
        else:
            outer_extra_thickness = 0

    if enable_magnet:
        magnet_slot_radius = magnet_radius + magnet_radius_padding
        magnet_slot_height = magnet_height + magnet_height_padding
        front_back_reserve_space += magnet_slot_radius * 2 + wall_thickness

    outer_thickness = (
        wall_thickness + friction_part_thickness + outer_extra_thickness
    )  # mm
    friction_space_on_body = friction_part_thickness + friction_gap  # mm
    front_back_thickness = outer_thickness + front_back_reserve_space  # mm
    left_right_thickness = outer_thickness + left_right_reserve_space  # mm
    single_slot_main_space = pick_thickness + slot_padding * 2
    single_slot_space = single_slot_main_space + slot_open
    slot_spacing = single_slot_space + wall_thickness
    slot_width = pick_width * slot_width_ratio
    upper_ratio = 1 - lower_ratio
    slot_height = pick_depth * math.cos(math.radians(slot_tilt))
    slot_lower_height = slot_height * lower_ratio
    slot_front_length = lower_ratio * pick_depth * math.sin(math.radians(slot_tilt))
    pick_typical_tilt = math.degrees(
        math.atan2(slot_open + slot_front_length, slot_lower_height)
    )
    pick_back_length = (
        upper_ratio * pick_depth * math.sin(math.radians(pick_typical_tilt))
    )
    total_slots_length = (
        slots_per_row * single_slot_space
        + (slots_per_row - 1) * wall_thickness
        + pick_back_length
    )
    slots_raw_spacing = pick_width + wall_thickness + slot_row_extra_spacing
    total_slots_width = pick_width * slots_rows + (
        wall_thickness + slot_row_extra_spacing
    ) * (slots_rows - 1)
    total_length = (
        total_slots_length
        + front_back_thickness
        + max(slot_front_length + wall_thickness, front_back_thickness)
    )
    total_width = total_slots_width + left_right_thickness * 2
    lower_height = slot_lower_height + wall_thickness
    upper_height = slot_height * upper_ratio + wall_thickness
    if enable_buckle:
        friction_depth = buckle_edge_distance * 2 + friction_chamfer_depth
    elif enable_magnet:
        friction_depth = friction_chamfer_depth * 2
    else:
        friction_depth = lower_height * 0.5

    assert buckle_edge_distance * 2 > buckle_height, "incomplete buckle"
    assert (
        upper_case_inner_fillet_radius * 2 < wall_thickness + slot_row_extra_spacing
    ), "invalid case inner fillet"

    body = Part()
    body_face = Rectangle(total_length, total_width)
    body_main = extrude(body_face, amount=lower_height)
    body += body_main
    body_top_face = body.faces().sort_by(Axis.Z).last

    # slots air
    slots_row_air = Part()
    pick_slot_air = Part()
    slot_tilt_reserve_height = (
        math.sin(math.radians(slot_tilt)) * single_slot_main_space / 2.0
    )
    air_curve = Spline(
        [
            (-slot_width / 2.0, -slot_tilt_reserve_height),
            # (-slot_width / 2.0, 0),
            (0, pick_depth * lower_ratio),
            # (slot_width / 2.0, 0),
            (slot_width / 2.0, -slot_tilt_reserve_height),
        ],
    )
    pick_slot_face = slot_sweep_face(
        slot_width, single_slot_main_space, slot_tilt=slot_tilt, slot_open=slot_open
    )
    sweep_face = (
        Rotation(Z=-90)
        * Pos(Y=slot_width / 2.0)
        * split(pick_slot_face, bisect_by=Plane.XZ)
    )
    sweep_curve = (
        Rotation(Z=-90) * Rotation(X=-90) * split(air_curve, bisect_by=Plane.YZ)
    )
    swept = sweep(
        (sweep_curve ^ 0) * sweep_face,
        sweep_curve,
        is_frenet=True,
    )
    swept = split(swept, Plane.XZ)
    pick_slot_air += Rotation(Y=-slot_tilt) * (swept + swept.mirror(Plane.XZ))
    pick_slot_air = split(pick_slot_air, Plane.XY, keep=Keep.BOTTOM)
    slot_center_x = (
        front_back_thickness + pick_back_length + single_slot_space / 2 + slot_open
    )
    for slot_index in range(slots_per_row):
        slots_row_air += Pos(X=slot_center_x) * pick_slot_air
        slot_center_x += slot_spacing

    slots_rows_air = Part()
    row_locations = GridLocations(0, slots_raw_spacing, 1, slots_rows)
    slots_rows_air += row_locations * slots_row_air

    # friction part
    def make_friction_style_part(thickness):
        part = Part()
        rect = Rectangle(total_length - thickness * 2, total_width - thickness * 2)
        face = Rectangle(total_length, total_width) - rect
        part += extrude(face, amount=-friction_depth)
        return part

    # friction air
    friction_air = make_friction_style_part(friction_space_on_body)

    # magnet
    if enable_magnet:
        magnet_slot = Part()
        magnet_slot = Cylinder(radius=magnet_slot_radius, height=magnet_slot_height)
        magnet_x_count = 2
        magnet_slot_x_total_space = (
            total_length
            - (friction_part_thickness + wall_thickness + magnet_slot_radius) * 2
        )
        magnet_slot_y_total_space = (
            total_width
            - (friction_part_thickness + wall_thickness + +magnet_slot_radius) * 2
        )
        magnet_locations = GridLocations(
            magnet_slot_x_total_space,
            magnet_slot_y_total_space / (magnet_y_count - 1),
            2,
            magnet_y_count,
        )
        magnet_total_number = magnet_x_count * magnet_y_count

        magnet = Part()
        magnet.label = "magnet"
        magnet.color = Color(0.75, 0.75, 0.75)  # silver
        magnet = Cylinder(radius=magnet_radius, height=magnet_height)
        magnet = fillet(magnet.edges(), radius=magnet_fillet_radius)
        RigidJoint(
            label="bottom",
            to_part=magnet,
            joint_location=Location(magnet.faces().sort_by(Axis.Z)[0].center()),
        )
        RigidJoint(
            label="top",
            to_part=magnet,
            joint_location=Location(magnet.faces().sort_by(Axis.Z)[-1].center()),
        )

    # buckle
    if enable_buckle:
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
    body = fillet(body.edges().group_by(Axis.Z)[0], radius=body_bottom_fillet_radius)
    middle_edges = body.edges().filter_by(Plane.XY).group_by(Axis.Z)[-2]
    middle_outer_edges = rectangle_donut_outer_edges(middle_edges)
    body = fillet(middle_outer_edges, radius=anti_pinch_fillet_radius)
    body = chamfer(
        body.edges().group_by(Axis.Z)[-1],
        length2=friction_chamfer,
        length=friction_chamfer_depth,
    )
    remove_slot_air = Pos(X=-total_length / 2.0, Z=lower_height) * slots_rows_air
    edge_snapshot = body.edges()
    body -= remove_slot_air
    slot_open_edges = (body.edges() - edge_snapshot).group_by(Axis.Z)[-1]
    body = fillet(slot_open_edges, radius=slot_open_fillet)
    if enable_buckle:
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
    if enable_magnet:
        edge_snapshot = body.edges()
        body_magnet_slot = fillet(
            magnet_slot.edges().group_by(Axis.Z)[0],
            radius=magnet_slot_inner_fillet_radius,
        )
        body -= (
            Pos(Z=lower_height - magnet_slot_height / 2.0)
            * magnet_locations
            * body_magnet_slot
        )
        body = fillet(
            (body.edges() - edge_snapshot).group_by(Axis.Z)[-1],
            radius=magnet_slot_outer_fillet_radius,
        )
        magnet_location_index = 0
    if enable_magnet:
        for location in Pos(Z=lower_height - magnet_slot_height) * magnet_locations:
            RigidJoint(
                f"magnet_mount_{magnet_location_index}",
                to_part=body,
                joint_location=location,
            )
            magnet_location_index += 1
    RigidJoint("case_mount", to_part=body, joint_location=Pos(Z=lower_height))

    # upper case
    upper_case = Part()
    upper_case = extrude(body_face, amount=upper_height)
    friction_part = make_friction_style_part(friction_part_thickness)
    upper_case += friction_part
    upper_case = fillet(upper_case.edges().filter_by(Axis.Z), radius=body_fillet_radius)
    upper_case = fillet(
        upper_case.edges().group_by(Axis.Z)[-1], radius=upper_case_top_fillet_radius
    )
    upper_case = fillet(
        rectangle_donut_outer_edges(upper_case.edges().group_by(Axis.Z)[0]),
        radius=anti_pinch_fillet_radius,
    )
    upper_case_air = Part()
    upper_case_row_air = extrude(
        Rectangle(
            total_length - front_back_thickness * 2,
            slot_width,
        ),
        amount=upper_height - wall_thickness,
    )
    upper_case_row_air = fillet(
        upper_case_row_air.edges().group_by(Axis.Z)[-2], radius=body_fillet_radius
    )
    upper_case_row_air = fillet(
        upper_case_row_air.edges().group_by(Axis.Z)[-1], radius=body_fillet_radius
    )
    upper_case_air += row_locations * upper_case_row_air
    edge_snapshot = upper_case.edges()
    upper_case = upper_case - upper_case_air
    upper_case = fillet(
        (upper_case.edges() - edge_snapshot).group_by(Axis.Z)[0],
        radius=upper_case_inner_fillet_radius,
    )

    if enable_buckle:
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
    if enable_magnet:
        edge_snapshot = upper_case.edges()
        upper_case_magnet_slot = fillet(
            magnet_slot.edges().group_by(Axis.Z)[-1],
            radius=magnet_slot_inner_fillet_radius,
        )
        upper_case -= (
            Pos(Z=magnet_slot_height / 2.0) * magnet_locations * upper_case_magnet_slot
        )
        upper_case = fillet(
            (upper_case.edges() - edge_snapshot).group_by(Axis.Z)[0],
            radius=magnet_slot_outer_fillet_radius,
        )
        magnet_location_index = 0
        for location in Pos(Z=magnet_slot_height) * magnet_locations:
            RigidJoint(
                f"magnet_mount_{magnet_location_index}",
                to_part=upper_case,
                joint_location=location,
            )
            magnet_location_index += 1
    LinearJoint("bottom", to_part=upper_case, axis=Axis.Z, linear_range=(-math.inf, 0))

    if enable_watermark:
        watermark_line1 = f"Yinfeng's"
        watermark_line2 = f"Prototype {datetime.datetime.now()}"
        line_spacing = 7
        watermark = Part()
        watermark_depth = wall_thickness / 2
        watermark += Pos(Y=-line_spacing / 2) * extrude(
            Text(watermark_line2, font_size=5), amount=watermark_depth
        )
        watermark += Pos(Y=line_spacing / 2) * extrude(
            Text(watermark_line1, font_size=5), amount=watermark_depth
        )
        body -= Pos(Z=watermark_depth) * Rotation(X=180) * watermark
        upper_case -= Pos(Z=upper_height - watermark_depth) * watermark

    body.label = "body"
    upper_case.label = "case"
    assembly_body = copy(body)
    assembly_upper_case = copy(upper_case)
    assembly_body.joints["case_mount"].connect_to(
        assembly_upper_case.joints["bottom"], position=0
    )
    assembly_body_magnets = []
    assembly_case_magnets = []
    if enable_magnet:
        for i in range(magnet_total_number):
            body_magnet = copy(magnet)
            body_magnet.label = f"body_magnet_{i}"
            assembly_body.joints[f"magnet_mount_{i}"].connect_to(
                body_magnet.joints["bottom"]
            )
            assembly_body_magnets.append(body_magnet)
            case_magnet = copy(magnet)
            case_magnet.label = f"case_magnet_{i}"
            assembly_upper_case.joints[f"magnet_mount_{i}"].connect_to(
                case_magnet.joints["top"]
            )
            assembly_case_magnets.append(case_magnet)
    full_body = Compound(
        label="full_body", children=[assembly_body] + assembly_body_magnets
    )
    full_upper_case = Compound(
        label="full_upper_case", children=[assembly_upper_case] + assembly_case_magnets
    )
    assembly = Compound(label="assembly", children=[full_body, full_upper_case])
    packed = pack([body, Rotation(X=180) * upper_case], padding=5, align_z=True)

    ov.show(assembly)

    print()
    total_volume = sum(part.volume for part in assembly.solids())
    print(f"volume: {total_volume} mm^3")

    output_directory = f"outputs/{code_name}"
    os.makedirs(output_directory, exist_ok=True)
    export_stl(body, f"{output_directory}/body-{code_name}.stl")
    export_stl(Rotation(X=180) * upper_case, f"{output_directory}/case-{code_name}.stl")
    export_step(assembly, f"{output_directory}/assembly-{code_name}.step")
    export_stl(Compound(packed), f"{output_directory}/pack-{code_name}.stl")
    return locals()


def main():
    return guitar_pick_case(
        auto_code_name=True,
        slots_per_row=15,
        slots_rows=1,
        pick_width=32,  # mm
        pick_depth=32,  # mm
        pick_thickness=2,  # mm
        slot_padding=0,  # mm
        slot_tilt=30,
        slot_open=1,  # mm
        slot_open_fillet=0.5,  # mm
        lower_ratio=0.5,
        body_bottom_fillet_radius=3,
        upper_case_top_fillet_radius=9,
        enable_magnet=True,
        magnet_y_count=3,
        enable_buckle=False,
        enable_watermark=False,
    )


if __name__ == "__main__":
    globals().update(main())
