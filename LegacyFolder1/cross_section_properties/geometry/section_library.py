# cross_section_properties/geometry/section_library.py

from typing import Tuple
from sectionproperties.pre.geometry import Geometry, CompoundGeometry
from cross_section_properties.geometry.utilities import rect_geom
import numpy as np

def i_beam(
    height: float, flange_width: float, web_thickness: float, flange_thickness: float,
    material, center: Tuple[float, float] = (0.0, 0.0)
) -> CompoundGeometry:
    h, b, tw, tf = height, flange_width, web_thickness, flange_thickness
    cx, cy = center
    # Bottom flange
    y0 = cy - h/2
    y1 = y0 + tf
    bot = rect_geom([(cx - b/2, y0), (cx + b/2, y0), (cx + b/2, y1), (cx - b/2, y1)], (cx, y0 + tf/2), material)
    # Top flange
    y3 = cy + h/2
    y2 = y3 - tf
    top = rect_geom([(cx - b/2, y2), (cx + b/2, y2), (cx + b/2, y3), (cx - b/2, y3)], (cx, y2 + tf/2), material)
    # Web
    x0 = cx - tw/2
    x1 = cx + tw/2
    web = rect_geom([(x0, y1), (x1, y1), (x1, y2), (x0, y2)], (cx, cy), material)
    return CompoundGeometry([bot, top, web])

def c_beam(
    height: float, flange_width: float, web_thickness: float, flange_thickness: float,
    material, center: Tuple[float, float] = (0.0, 0.0), orientation: str = "right"
) -> CompoundGeometry:
    # "right": C opens to the right; "left": opens to the left
    h, b, tw, tf = height, flange_width, web_thickness, flange_thickness
    cx, cy = center
    y0 = cy - h/2
    y1 = y0 + tf
    y3 = cy + h/2
    y2 = y3 - tf
    # Web always on the "left"
    if orientation == "right":
        x0 = cx - b/2
        x1 = x0 + tw
        # Bottom flange
        bot = rect_geom([(x0, y0), (x0 + b, y0), (x0 + b, y1), (x0, y1)], (cx, y0 + tf/2), material)
        # Top flange
        top = rect_geom([(x0, y2), (x0 + b, y2), (x0 + b, y3), (x0, y3)], (cx, y2 + tf/2), material)
        # Web
        web = rect_geom([(x0, y1), (x1, y1), (x1, y2), (x0, y2)], (x0 + tw/2, cy), material)
    else:  # left orientation
        x1 = cx + b/2
        x0 = x1 - tw
        bot = rect_geom([(x1 - b, y0), (x1, y0), (x1, y1), (x1 - b, y1)], (cx, y0 + tf/2), material)
        top = rect_geom([(x1 - b, y2), (x1, y2), (x1, y3), (x1 - b, y3)], (cx, y2 + tf/2), material)
        web = rect_geom([(x0, y1), (x1, y1), (x1, y2), (x0, y2)], (x1 - tw/2, cy), material)
    return CompoundGeometry([bot, top, web])

def box_section(
    height: float, width: float, thickness: float, material, center: Tuple[float, float] = (0.0, 0.0)
) -> Geometry:
    from cross_section_properties.geometry.hollow import true_hollow_skin
    cx, cy = center
    hw, hh = width / 2, height / 2
    n = 4
    outer = [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh)]
    return true_hollow_skin(outer, thickness, material, control_point=center)

def circle_section(
    radius: float, thickness: float, material, n_points: int = 64, center: Tuple[float, float] = (0.0, 0.0)
) -> Geometry:
    from cross_section_properties.geometry.hollow import true_hollow_skin
    cx, cy = center
    theta = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    outer = [(cx + radius * np.cos(t), cy + radius * np.sin(t)) for t in theta]
    return true_hollow_skin(outer, thickness, material, control_point=center)
