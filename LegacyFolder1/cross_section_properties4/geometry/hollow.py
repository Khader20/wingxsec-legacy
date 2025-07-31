from sectionproperties.pre.geometry import Geometry
from shapely.geometry import Polygon
from typing import List, Tuple

def offset_polygon(points: List[Tuple[float, float]], thickness: float) -> List[Tuple[float, float]]:
    poly = Polygon(points)
    inner = poly.buffer(-thickness, join_style=2, cap_style=2)
    if inner.is_empty:
        raise ValueError("Thickness too large, polygon disappears.")
    return list(inner.exterior.coords)[:-1]

def true_hollow_skin(
    outer_points: List[Tuple[float, float]],
    skin_thickness: float,
    material,
    control_point: Tuple[float, float] = (0.5, 0.0)
) -> Geometry:
    """
    Builds a skin-only (hollow) airfoil as a single ring-shaped polygon for sectionproperties.
    """
    inner_points = offset_polygon(outer_points, skin_thickness)
    n_outer = len(outer_points)
    n_inner = len(inner_points)

    # Polygon points: outer (CCW) + inner (CW)
    polygon_points = outer_points + inner_points[::-1]

    # Facets: outer perimeter
    outer_facets = [(i, i + 1) for i in range(n_outer - 1)] + [(n_outer - 1, 0)]
    # Facets: inner perimeter (after outer, indexes offset by n_outer)
    inner_facets = [(n_outer + i, n_outer + i + 1) for i in range(n_inner - 1)] + \
                   [(n_outer + n_inner - 1, n_outer)]
    facets = outer_facets + inner_facets

    return Geometry.from_points(
        points=polygon_points,
        facets=facets,
        control_points=[control_point],
        holes=[],
        material=material
    )









import numpy as np
from shapely.geometry import LineString, Polygon
from sectionproperties.pre.geometry import Geometry, CompoundGeometry

def find_spar_intersection(airfoil_pts, x_spar):
    """
    Given ordered airfoil_pts, return intersection y coords at x_spar.
    Returns (y_bottom, y_top)
    """
    airfoil_poly = Polygon(airfoil_pts)
    spar_line = LineString([(x_spar, -10), (x_spar, 10)])  # long vertical
    intersections = airfoil_poly.boundary.intersection(spar_line)
    if intersections.is_empty:
        raise ValueError("Spar does not intersect airfoil at this chordwise location.")
    if intersections.geom_type == 'MultiPoint':
        ys = [p.y for p in intersections.geoms]
    else:
        ys = [intersections.y]
    ys = sorted(ys)
    if len(ys) < 2:
        raise ValueError("Vertical at x_spar did not intersect airfoil in two places.")
    return ys[0], ys[-1]

def add_spar_to_airfoil_skin(
    skin_geom: Geometry,
    airfoil_pts: list,
    x_spar: float,
    t_spar: float,
    mat_spar,
    n_spar_points: int = 4
) -> CompoundGeometry:
    """
    Add a spar at x_spar (chordwise), width t_spar, full height to airfoil contour.
    Returns CompoundGeometry (skin + spar).
    """
    y_bot, y_top = find_spar_intersection(airfoil_pts, x_spar)
    # Create spar rectangle centered at x_spar
    x0 = x_spar - t_spar / 2
    x1 = x_spar + t_spar / 2
    spar_pts = [(x0, y_bot), (x1, y_bot), (x1, y_top), (x0, y_top)]
    spar_facets = [(i, i+1) for i in range(3)] + [(3, 0)]
    spar_cp = [(x_spar, (y_bot + y_top) / 2)]
    spar_geom = Geometry.from_points(spar_pts, spar_facets, spar_cp, material=mat_spar)
    return CompoundGeometry([skin_geom, spar_geom])
