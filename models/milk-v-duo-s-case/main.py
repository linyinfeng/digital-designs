# %% [markdown]
# Milk-V Duo S Case

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

script_path = os.path.dirname(os.path.abspath(__file__))
original_board = import_step(os.path.join(script_path, "reference/duo_s_pcb_3d.stp"))

# %%

original_board.label = "Milk-V Duo S"

# %% [markdown]
# - Origin is the pin 26 of the GPIO
# - X axis goes along the longer side of the board
# - Y axis goes along the shorter side of the board
#
# See:
# - <https://milkv.io/docs/duo/getting-started/duos>
# - <https://github.com/milkv-duo/duo-files/blob/main/duo-s/hardware/DUO_S_MB_V1_2-TOP.pdf>

# %%


class Config:
    def __init__(self):
        self.fill_truth()
        self.custom()
        self.complete()

    def fill_truth(self):
        # square PCB (the IO side is longer due to the slots)
        self.mounting_hole_distance = Decimal("38.10")
        self.board_edge_distance = Decimal("43.18")
        self.mounting_hole_diameter_inner = Decimal("2.50")
        self.mounting_hole_diameter_outer = (
            self.board_edge_distance - self.mounting_hole_distance
        )
        self.gpio_columns = 13
        self.gpio_lines = 2
        self.gpio_pin_distance = Decimal("2.54")
        self.gpio_column_length = self.gpio_columns * self.gpio_pin_distance
        self.gpio_center_to_edge = (
            self.gpio_column_length / 2 + self.mounting_hole_diameter_outer
        )
        self.origin_gpio_to_edge_x = (
            self.gpio_pin_distance / 2 + self.mounting_hole_diameter_outer
        )
        self.origin_gpio_to_edge_y = self.gpio_pin_distance / 2 * 3
        self.edge_to_io_face_distance = Decimal("4.75")
        self.edge_to_type_c_face_distance = Decimal("1.5")
        assert self.gpio_center_to_edge == Decimal("21.59")
        self.pcb_thickness = Decimal("1.6")

        self.poe_to_edge_y = Decimal("5.46")
        self.poe_to_edge_x = Decimal("0.28")

        self.csi_j1_slot_length = Decimal("8.0")  # 16-pin 0.5mm pitch
        self.csi_j1_slot_to_edge_x = Decimal("20.53")
        self.csi_j1_slot_to_edge_y = Decimal("8.72")  # estimated
        self.csi_j2_slot_length = Decimal("15.0")  # 15-pin 1.0mm pitch
        self.csi_j2_slot_to_edge_x = Decimal("15.11")
        self.csi_j2_slot_to_edge_y = Decimal("8.40")  # estimated

        self.type_c_to_edge = Decimal("17.5")
        self.type_c_height = Decimal("3.16")  # estimated
        self.type_c_width = Decimal("8.94")  # estimated
        self.type_c_radius = Decimal("1.28")  # estimated

        self.micro_switch_1_to_edge = Decimal("8.03")
        self.micro_switch_2_to_edge = Decimal("14.32")
        self.micro_switch_radius = Decimal("1.0")
        self.micro_switch_center_y = Decimal("1.6")  # estimated

        self.os_toggle_to_edge = Decimal("13.168")  # 3d model
        # self.os_toggle_to_edge = Decimal("12.925") # dxf
        self.os_toggle_slot_length = Decimal("5")
        self.os_toggle_height = Decimal("1.3")  # estimated
        self.os_toggle_center_y = -(
            Decimal("0.15") + self.os_toggle_height / 2
        )  # estimated

        self.tf_to_edge = Decimal("12.755")  # 3d model
        # self.tf_to_edge = Decimal("12.24") # dxf
        self.tf_height = Decimal("1.32")
        self.tf_slot_width = Decimal("12")
        self.tf_finger_space = Decimal("5.0")

        self.ethernet_to_edge = Decimal("17.155")  # 3d model
        # self.ethernet_to_edge = Decimal("16.645") # dxf
        self.ethernet_height = Decimal("13.50")
        self.ethernet_width = Decimal("15.93")
        self.ethernet_length = Decimal("21.250")

        self.usb_a_to_edge = Decimal("12.02")  # 3d model
        # self.usb_a_to_edge = Decimal("11.78")
        self.usb_a_height = Decimal("13.1")
        self.usb_a_bottom_height = Decimal("0.7")
        self.usb_a_width = Decimal("5.7")
        self.usb_a_ear_size = Decimal("0.65")
        self.usb_a_ear_thickness = Decimal("0.3")

        self.dupont_connector_head_length = Decimal("14")
        self.pin_head_height = Decimal("2.5")
        self.dupont_connector_head_top = (
            self.dupont_connector_head_length + self.pin_head_height
        )

    def custom(self):
        self.accuracy = Decimal("0.2")
        self.wall_thickness = self.edge_to_type_c_face_distance - self.accuracy
        self.extra_bottom_space = Decimal("1.0")
        assert self.extra_bottom_space >= self.accuracy
        self.extra_top_space = Decimal("1.5")
        self.box_inner_radius = self.mounting_hole_diameter_outer / 2 + self.accuracy
        self.box_outer_radius = (
            self.mounting_hole_diameter_outer / 2 + self.accuracy + self.wall_thickness
        )
        self.heat_dissipation_slot_width = Decimal("2.0")
        self.heat_dissipation_slot_length = Decimal("20.0")
        self.heat_dissipation_slot_spacing_x = self.heat_dissipation_slot_width
        self.heat_dissipation_slot_spacing_y = self.heat_dissipation_slot_spacing_x
        self.bottom_heat_dissipation_slot_locations = GridLocations(
            x_spacing=f(
                self.heat_dissipation_slot_length + self.heat_dissipation_slot_spacing_x
            ),
            y_spacing=f(
                self.heat_dissipation_slot_width + self.heat_dissipation_slot_spacing_y
            ),
            x_count=2,
            y_count=8,
        )
        self.csi_slot_width = Decimal("1.0")
        self.csi_slot_extra_length = Decimal("2.0")
        self.antenna_clip_width = Decimal("3.0")
        self.os_toggle_install_angle = 45

        # M2.5x10 screw
        self.screw_outer_diameter = Decimal("2.5")
        self.screw_drill_diameter = Decimal("2.1")
        self.screw_head_thickness = Decimal("1.5")
        self.screw_head_diameter = Decimal("4.1")

        # GPIO insert helper
        # self.gpio_guard_depth = self.extra_top_space - self.accuracy
        self.gpio_guard_depth = Decimal("5.0")
        self.gpio_hand_chamfer_size = (
            self.wall_thickness - self.accuracy
        )  # just chamfer to wall thickness

        self.cut_line_radius = Decimal("2.5")
        self.cut_line_left_lift_to = self.micro_switch_center_y
        self.cut_line_right_lift_to = self.usb_a_bottom_height - self.accuracy

    def complete(self):
        pass

    def dump_info(self):
        print(f"Mounting hole distance: {self.mounting_hole_diameter_outer}mm")
        print(f"GPIO length: {self.gpio_column_length}mm")
        print(f"First GPIO to edge (X): {self.origin_gpio_to_edge_x}mm")
        print(f"First GPIO to edge (Y): {self.origin_gpio_to_edge_y}mm")
        print(f"Wall thickness: {self.wall_thickness}mm")
        print(
            f"Antenna space: {self.extra_top_space - self.accuracy * 3 - self.wall_thickness}mm"
        )
        print(
            f"Dupont connector head top: {self.dupont_connector_head_length + self.pin_head_height}mm"
        )


config: Config = Config()
config.dump_info()

# %%

# adjust board center

original_board_center = Vector(
    (
        (f(config.board_edge_distance) / 2.0 - f(config.origin_gpio_to_edge_x)),
        ((f(config.board_edge_distance) / 2.0 - f(config.origin_gpio_to_edge_y))),
        0,
    )
)
board = original_board.move(
    Location((-original_board_center.X, -original_board_center.Y, 0))
)
bbox = board.bounding_box()
show(board, bbox)

# %%

show_list = []

# %%

with BuildPart() as case_builder:
    show_list = [board, case_builder]

    case_builder.label = "Milk-V Duo S Case"
    with BuildSketch(
        Plane.XY.move(Location(bbox.min)).offset(-f(config.extra_bottom_space))
    ) as bottom:
        Rectangle(bbox.size.X, bbox.size.Y, align=Align.MIN)
    extrude(amount=-f(config.wall_thickness))

    faces = case_builder.faces().filter_by(Plane.XZ)
    extruded = extrude(faces, amount=f(config.accuracy + config.wall_thickness))
    bottom_faces = case_builder.faces().filter_by(Plane.XY).sort_by(Axis.Z)
    bottom_inner_face = bottom_faces[-1]
    bottom_outer_face = bottom_faces[0]
    face_bbox = bottom_inner_face.bounding_box()
    with BuildSketch(bottom_inner_face) as walls_builder:
        Rectangle(face_bbox.size.X, face_bbox.size.Y)
        RectangleRounded(
            face_bbox.size.X - f(config.wall_thickness) * 2,
            face_bbox.size.Y - f(config.wall_thickness) * 2,
            radius=f(config.box_inner_radius),
            mode=Mode.SUBTRACT,
        )
    inner_space_z = (
        bbox.max.Z - bottom_inner_face.center().Z + f(config.extra_top_space)
    )
    extrude(amount=inner_space_z)
    inner_wall_faces_yz = (
        case_builder.faces(Select.LAST).filter_by(Plane.YZ).sort_by(Axis.X)[1:-1]
    )
    left_inner_face = inner_wall_faces_yz[0]
    right_inner_face = inner_wall_faces_yz[-1]
    top_inner_face = bottom_inner_face.moved(Location((0, 0, inner_space_z)))
    add(top_inner_face)
    extrude(amount=f(config.wall_thickness))
    top_outer_face = (
        case_builder.faces().filter_by(Plane.XY).sort_by(Axis.Z, reverse=True)[0]
    )
    print(f"Top outer face Z: {top_outer_face.center().Z}mm")

    # Mounting pillar
    mounting_pillar_locations = GridLocations(
        x_spacing=f(config.mounting_hole_distance),
        y_spacing=f(config.mounting_hole_distance),
        x_count=2,
        y_count=2,
    )
    with BuildPart():
        with BuildSketch(Plane.XY.offset(bottom_inner_face.center().Z)):
            with mounting_pillar_locations:
                Circle(f(config.mounting_hole_diameter_outer / 2 + config.accuracy))
        extrude(amount=inner_space_z)

    # Mounting Pillar hole
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(
            Plane.XY.offset(bottom_inner_face.center().Z)
        ) as mounting_pillar_hole_sketch:
            with mounting_pillar_locations:
                Circle(f(config.screw_drill_diameter / 2))  # no accuracy here (tapping)
        extrude(amount=inner_space_z)
        extrude(mounting_pillar_hole_sketch.sketch, amount=-f(config.wall_thickness))

    # Screw head clearance
    with BuildPart(Plane.XY.offset(bottom_outer_face.center().Z), mode=Mode.SUBTRACT):
        with mounting_pillar_locations:
            Cone(
                bottom_radius=f(config.screw_head_diameter / 2 + config.accuracy),
                top_radius=f(
                    config.screw_drill_diameter / 2
                ),  # no accuracy here (tapping)
                height=f(config.screw_head_thickness + config.accuracy),
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # PCB cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(Plane.XY) as pcb_xy_sketch:
            RectangleRounded(
                f(config.board_edge_distance + config.accuracy),
                f(config.board_edge_distance + config.accuracy),
                radius=f(config.mounting_hole_diameter_outer / 2 + config.accuracy),
            )
        extrude(amount=-f(config.pcb_thickness + config.accuracy))
        extrude(pcb_xy_sketch.sketch, amount=f(config.accuracy))

    # Bottom heat dissipation slots
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(bottom_inner_face):
            with config.bottom_heat_dissipation_slot_locations:
                SlotOverall(
                    f(config.heat_dissipation_slot_length),
                    f(config.heat_dissipation_slot_width),
                )
        extrude(amount=-f(config.wall_thickness))

    # Top heat dissipation slots
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(top_inner_face):
            with Locations(
                (
                    -f(
                        config.heat_dissipation_slot_length
                        + config.heat_dissipation_slot_spacing_x
                    )
                    / 2,
                    0,
                )
            ):
                with GridLocations(
                    x_spacing=0,
                    y_spacing=f(
                        config.heat_dissipation_slot_width
                        + config.heat_dissipation_slot_spacing_y
                    ),
                    x_count=1,
                    y_count=5,
                ):
                    SlotOverall(
                        f(config.heat_dissipation_slot_length),
                        f(config.heat_dissipation_slot_width),
                    )
        extrude(amount=f(config.wall_thickness))

    # GPIO guards
    top_cutout_plane = Plane.XY.offset(top_inner_face.center().Z)
    gpio_locations = GridLocations(
        0,
        f(2 * (config.board_edge_distance / 2 - config.gpio_pin_distance)),
        1,
        2,
    )
    gpio_length = config.gpio_columns * config.gpio_pin_distance
    gpio_width = config.gpio_lines * config.gpio_pin_distance
    with BuildPart():
        with BuildSketch(top_cutout_plane) as gpio_cutout_sketch:
            with gpio_locations:
                Rectangle(
                    f(gpio_length + 2 * config.wall_thickness + 2 * config.accuracy),
                    f(gpio_width + 2 * config.wall_thickness + 2 * config.accuracy),
                )
        extrude(amount=-f(config.gpio_guard_depth))

    # POE guards
    poe_locations = Locations(
        (
            f(
                config.board_edge_distance / 2
                - config.poe_to_edge_x
                - 2 * config.gpio_pin_distance
            ),
            f(
                -config.board_edge_distance / 2
                + config.poe_to_edge_y
                + config.gpio_pin_distance / 2
            ),
        )
    )
    poe_length = 4 * config.gpio_pin_distance
    poe_width = config.gpio_pin_distance
    with BuildPart():
        with BuildSketch(top_cutout_plane) as poe_cutout_sketch:
            with poe_locations:
                Rectangle(
                    f(poe_length + 2 * config.wall_thickness + 2 * config.accuracy),
                    f(poe_width + 2 * config.wall_thickness + 2 * config.accuracy),
                )
        extrude(amount=-f(config.gpio_guard_depth))

    # GPIO cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(top_cutout_plane) as gpio_cutout_sketch:
            with gpio_locations:
                Rectangle(
                    f(gpio_length + 2 * config.accuracy),
                    f(gpio_width + 2 * config.accuracy),
                )
        extrude(amount=f(config.wall_thickness))
        extrude(gpio_cutout_sketch.sketch, amount=-inner_space_z)  # also cut pillars

    # POE cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(top_cutout_plane) as poe_cutout_sketch:
            with poe_locations:
                Rectangle(
                    f(poe_length + 2 * config.accuracy),
                    f(poe_width + 2 * config.accuracy),
                )
        extrude(amount=f(config.wall_thickness))
        extrude(poe_cutout_sketch.sketch, amount=-inner_space_z)  # also cut pillars

    # Outer rounded edges
    with BuildPart(mode=Mode.INTERSECT):
        with BuildSketch(bottom_inner_face):
            RectangleRounded(
                face_bbox.size.X, face_bbox.size.Y, radius=f(config.box_outer_radius)
            )
        extrude(amount=inner_space_z + f(config.wall_thickness), both=True)

    # Antenna clip
    poe_bbox = poe_cutout_sketch.sketch.bounding_box()
    with BuildSketch(Plane.XY.offset(f(config.ethernet_height + config.accuracy))):
        with BuildLine():
            l1 = Line(
                (poe_bbox.min.X, poe_bbox.max.Y + f(config.wall_thickness)),
                (bbox.max.X, poe_bbox.max.Y + f(config.wall_thickness)),
            )
            l2 = Line(l1 @ 1, l1 @ 1 + (0.0, f(config.antenna_clip_width)))
            l3 = Line(l2 @ 1, l1 @ 0)
        make_face()
    extrude(amount=f(config.wall_thickness))
    front_wall_face = case_builder.faces(Select.LAST).filter_by(Plane.XZ)[0]
    front_wall = extrude(front_wall_face, amount=f(config.wall_thickness))
    extrude(
        front_wall.faces().filter_by(Plane.XY).sort_by(Axis.Z)[-1], until=top_inner_face
    )

    # CSI cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(top_cutout_plane):
            # J1
            with Locations(
                (
                    f(config.board_edge_distance / 2 - config.csi_j1_slot_to_edge_x),
                    f(config.board_edge_distance / 2 - config.csi_j1_slot_to_edge_y),
                )
            ):
                Rectangle(
                    f(
                        config.csi_j1_slot_length
                        + config.csi_slot_extra_length
                        + 2 * config.accuracy
                    ),
                    f(config.csi_slot_width + 2 * config.accuracy),
                )
            # J2
            with Locations(
                (
                    f(-config.board_edge_distance / 2 + config.csi_j2_slot_to_edge_x),
                    f(-config.board_edge_distance / 2 + config.csi_j2_slot_to_edge_y),
                )
            ):
                Rectangle(
                    f(
                        config.csi_j2_slot_length
                        + config.csi_slot_extra_length
                        + 2 * config.accuracy
                    ),
                    f(config.csi_slot_width + 2 * config.accuracy),
                )
        extrude(amount=f(config.wall_thickness))

    left_cutout_plane = Plane(left_inner_face).move(
        Location((0, 0, -left_inner_face.center().Z))
    )
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(left_cutout_plane):
            # Type C port cutout
            with Locations(
                (
                    f(config.board_edge_distance / 2 - config.type_c_to_edge),
                    f(config.type_c_height / 2),
                )
            ):
                RectangleRounded(
                    f(config.type_c_width + 2 * config.accuracy),
                    f(config.type_c_height + 2 * config.accuracy),
                    radius=f(config.type_c_radius + config.accuracy),
                )
            # Micro switch cutout
            with Locations(
                (
                    f(-config.board_edge_distance / 2 + config.micro_switch_1_to_edge),
                    f(config.micro_switch_center_y),
                ),
                (
                    f(-config.board_edge_distance / 2 + config.micro_switch_2_to_edge),
                    f(config.micro_switch_center_y),
                ),
            ):
                Circle(f(config.micro_switch_radius + config.accuracy))
        extrude(amount=-f(config.wall_thickness))

    # OS toggle cutout
    with BuildPart(left_cutout_plane, mode=Mode.SUBTRACT):
        with Locations(
            (
                f(config.board_edge_distance / 2 - config.os_toggle_to_edge),
                f(-config.pcb_thickness + config.os_toggle_center_y),
            )
        ):
            length = f(config.os_toggle_slot_length + 2 * config.accuracy)
            height = f(config.os_toggle_height + 2 * config.accuracy)
            with Locations(
                Pos(length / 2, -height / 2, -f(config.wall_thickness))
                * Rotation(X=-90, Z=180)
            ):
                Wedge(
                    xsize=length,
                    ysize=f(config.wall_thickness),
                    zsize=height,
                    xmin=0.0,
                    zmin=0.0,
                    xmax=length,
                    zmax=height
                    + f(config.wall_thickness)
                    * math.tan(math.radians(config.os_toggle_install_angle)),
                    align=(Align.MIN, Align.MIN, Align.MIN),
                )

    # SD card slot cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(left_cutout_plane):
            with Locations(
                (
                    f(-config.board_edge_distance / 2 + config.tf_to_edge),
                    f(-config.pcb_thickness - config.tf_height / 2),
                )
            ):
                Rectangle(
                    f(config.tf_slot_width + 2 * config.accuracy),
                    f(config.tf_height + 2 * config.accuracy),
                )
        extrude(amount=-f(config.wall_thickness))
        # TODO fingertip space

    right_cutout_plane = (
        Plane(right_inner_face)
        .move(Location((0, 0, -right_inner_face.center().Z)))
        .rotated((180, 0, 0))
    )
    # Ethernet cutout
    with BuildPart(mode=Mode.SUBTRACT):
        with BuildSketch(right_cutout_plane) as ethernet_cutout_sketch:
            with Locations(
                (
                    f(config.board_edge_distance / 2 - config.ethernet_to_edge),
                    f(config.ethernet_height / 2),
                )
            ):
                Rectangle(
                    f(config.ethernet_width + config.accuracy * 2),
                    f(config.ethernet_height + config.accuracy * 2),
                )
        extrude(amount=-f(config.wall_thickness))
        extrude(
            ethernet_cutout_sketch.sketch, amount=config.ethernet_length
        )  # cut the gpio and poe guards

    # USB A cutout
    with BuildPart(mode=Mode.SUBTRACT):
        center_location = Locations(
            (
                f(-config.board_edge_distance / 2 + config.usb_a_to_edge),
                f(config.usb_a_bottom_height + config.usb_a_height / 2),
            )
        )
        with BuildSketch(right_cutout_plane):
            with center_location:
                Rectangle(
                    f(config.usb_a_width + config.accuracy * 2),
                    f(config.usb_a_height + config.accuracy * 2),
                )
        extrude(amount=-f(config.wall_thickness))
        with BuildSketch(right_cutout_plane.offset(-f(config.wall_thickness))):
            with center_location:
                Rectangle(
                    f(
                        config.usb_a_width
                        + config.usb_a_ear_size * 2
                        + config.accuracy * 2
                    ),
                    f(
                        config.usb_a_height
                        + config.usb_a_ear_size * 2
                        + config.accuracy * 2
                    ),
                )
        extrude(amount=f(config.usb_a_ear_thickness + config.accuracy))

show(*show_list, reset_camera=Camera.CENTER)

# %%

# Split
case_bbox = case_builder.part.bounding_box()
with BuildPart() as lower_case_mask_builder:
    with BuildSketch(Plane.XZ) as test:
        with BuildLine():
            begin = (case_bbox.min.X, f(config.cut_line_left_lift_to))
            left_radius = f(config.cut_line_left_lift_to) / 2
            l1 = Line(begin, (begin[0] + f(config.box_outer_radius) * 2, begin[1]))
            l2 = CenterArc(l1 @ 1 + (0, -left_radius), left_radius, 90, -90)
            l3 = CenterArc(l2 @ 1 + (left_radius, 0), left_radius, 180, 90)
            end = (case_bbox.max.X, f(config.cut_line_right_lift_to))
            right_radius = f(config.cut_line_right_lift_to) / 2
            l4 = Line((end[0] - f(config.box_outer_radius) * 2, end[1]), end)
            l5 = CenterArc(l4 @ 0 + (0, -right_radius), right_radius, 180, -90)
            l6 = CenterArc(l5 @ 0 + (-right_radius, 0), right_radius, -90, 90)
            l7 = Line(l3 @ 1, l6 @ 0)
            l8 = Line(end, (case_bbox.max.X, case_bbox.min.Z))
            l9 = Line(l8 @ 1, l8 @ 1 + (-case_bbox.size.X, 0))
            l10 = Line(l9 @ 1, l1 @ 0)
        make_face()
    extrude(amount=case_bbox.size.Y / 2, both=True)

lower_case = case_builder.part.intersect(lower_case_mask_builder.part)
lower_case.label = "Milk-V Duo S Lower Case"

upper_case = case_builder.part - lower_case_mask_builder.part
upper_case.label = "Milk-V Duo S Upper Case"

show_list = [board, lower_case, upper_case]

show(*show_list, reset_camera=Camera.CENTER)

# %%

total_volume = case_builder.part.volume * ureg.mm**3
pla_density = 1.24 * ureg.g / ureg.cm**3
print(f"Total volume: {total_volume}")
print(f"Estimated weight (PLA): {(total_volume * pla_density).to(ureg.g):.1f}")
