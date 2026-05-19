# %% [markdown]
# Rainbow Infinity

# %%

from build123d import *
from ocp_vscode import *
import math

# %%

def show_list(lst, locals, camera=Camera.KEEP):
    to_show = []
    for name in lst:
        to_show.append(locals[name])
    if "test" in locals:
        lst.append(locals["test"])
    show(*to_show, reset_camera=camera)

# %%

class Config:
    def __init__(self):
        self.radius = 20.0
        self.max_height = self.radius

        self.width = 5.0
        self.thickness = self.width / 2.0

        self.segments = 360

cfg = Config()

# %%

def build_q1_line():
    q1_xy = CenterArc((0, 0), cfg.radius, 0, 90)
    wall_face = sweep(q1_xy, Line((0, 0, 0), (0, 0, cfg.max_height)))
    q1_plane = Plane.XY * Pos(cfg.radius / 2, cfg.radius / 2)  * Rotation(Z=-45) * Rotation(X=45)
    splitted = split(wall_face, bisect_by=q1_plane, keep=Keep.BOTH)
    edges_diff = splitted.edges() - wall_face.edges()
    assert len(edges_diff) == 1
    return edges_diff[0]

q1_line = build_q1_line()

def build_main_path():
    q2_line = mirror(q1_line, Plane.XY).rotate(Axis.Z, 90)
    half_circle = q1_line + q2_line
    return half_circle + half_circle.rotate(Axis.Z, 180)

main_path = build_main_path()

# %%

def rotating_spline(begin_angle=0.0, distance=cfg.width / 2.0):
    pts = []
    for i in range(cfg.segments + 1):
        position = main_path @ (i / cfg.segments)
        circle_radian = math.radians(360.0 * i / cfg.segments)
        rotation_radian = begin_angle + circle_radian / 2.0
        radial = position.normalized()
        normal = position.cross(Vector(0, 0, 1))
        up = normal.cross(radial).normalized()
        offset = (radial * math.cos(rotation_radian) + up * math.sin(rotation_radian)) * distance
        pts.append(position + offset)
    return Spline(pts)

line1 = rotating_spline()
line2 = rotating_spline(math.pi)
line11, line12 = line1.split(Plane.XZ, keep=Keep.BOTH)
line21, line22 = line2.split(Plane.XZ, keep=Keep.BOTH)
connect_line1 = Line(line11 @ 0, line21 @ 0)
connect_line2 = Line(line11 @ 1, line21 @ 1)
wire1 = Wire([line11, line21, connect_line1, connect_line2])
wire2 = Wire([line12, line22, connect_line1, connect_line2])
face1 = Face.make_surface(wire1)
face2 = Face.make_surface(wire2)
infinity_face = face1 + face2
infinity = thicken(infinity_face, cfg.thickness / 2.0, both=True)

# %%

from pathlib import Path

script_directory = Path(__file__).resolve().parent
export_gltf(infinity, f"{script_directory}/../outputs/mobius-infinity.gltf")

# %%
