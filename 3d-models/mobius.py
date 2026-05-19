# %% [markdown]
# Mobius Strip

from build123d import *
import math
from numpy import linspace
from ocp_vscode import *

# 1. 定义基本参数
radius = 50.0       # 环的主半径
width = 20.0        # 莫比乌斯带的宽度
thickness = 3.0     # 莫比乌斯带的厚度
segments = 120      # 离散采样点数量，决定模型的平滑度

with BuildPart() as mobius_strip:
    # 2. 创建主路径：一个标准的圆周线 [1, 2]
    with BuildLine() as path:
        CenterArc((0, 0), radius, 0, 360)
    main_path = path.wire()

    # 3. 创建副法线导轨 (Binormal Guide Wire) [3, 4]
    # 核心逻辑：导轨线上的点相对于路径点产生旋转，从而锁定扫描截面的姿态。
    # 当路径绕行 360 度时，导轨定义的“向上”向量只旋转 180 度。
    guide_pts = []
    for i in range(segments + 1):
        # 当前角度 (0 到 2*PI)
        theta_rad = math.radians(360.0 * i / segments)
        # 旋转角度 (0 到 PI) —— 实现 180 度扭转
        phi_rad = theta_rad / 2.0

        # 路径上的点坐标
        p = Vector(radius * math.cos(theta_rad), radius * math.sin(theta_rad), 0)

        # 计算该位置的局部坐标向量
        # 我们在径向 (radial) 和 轴向 (Z轴) 之间进行插值以定义旋转
        radial = Vector(math.cos(theta_rad), math.sin(theta_rad), 0)
        up = Vector(0, 0, 1)

        # 构造参考向量（即副法线方向），偏移量 5.0 用于确保内核能识别方向
        v_ref = (radial * math.cos(phi_rad) + up * math.sin(phi_rad)) * 5.0
        guide_pts.append(p + v_ref)

    with BuildLine() as guide_line:
        Spline(guide_pts)
    binormal_guide = guide_line.wire()

    # 4. 创建扫描截面并对齐起点
    # 使用 ^ 运算符将工作平面精准对齐到路径的起始位置及其切线方向
    with BuildSketch(main_path ^ 0) as section:
        Rectangle(thickness, width)

    # 5. 执行带副法线控制的扫描 [5, 3]
    # binormal 参数强制截面的 Y 轴（或 X 轴）始终指向导轨线的对应点，
    # 从而解决传统 Frenet 框架下截面自转不受控的问题。
    sweep(path=main_path, binormal=binormal_guide, clean=True)

# 最终生成的 mobius_strip.part 是一个完整的莫比乌斯实体 [1]

show([section, main_path, mobius_strip])

# %%

guide_pts = [
    Vector(math.cos(a), math.sin(a), z)
    for z, a in zip(linspace(0, 10, 50), linspace(0, math.pi, 50))
]
guide_wire = Polyline(guide_pts).wire()
path_line = Line((0, 0, 0), (0, 0, 10))
section = Line((0, 0, 0), (1, 0, 0))
test = sweep(section, path=path_line, binormal=guide_wire)
show([section, path_line, guide_wire, test])
