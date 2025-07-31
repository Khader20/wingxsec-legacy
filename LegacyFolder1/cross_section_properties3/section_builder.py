import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from sectionproperties.pre import CompoundGeometry


def get_spar_polygon(airfoil_poly, x_c, thickness, height_fraction=1.0):
    """
    Return a shapely Polygon for a spar at x_c, height auto-fit to airfoil.
    """
    bounds = airfoil_poly.bounds
    line = LineString([(x_c, bounds[1] - 1.0), (x_c, bounds[3] + 1.0)])
    inter = airfoil_poly.intersection(line)
    if inter.is_empty:
        raise ValueError(f"Spar at x={x_c:.3f} does not intersect airfoil.")
    ys = []
    if inter.geom_type == "MultiPoint":
        ys = sorted(pt.y for pt in inter.geoms)
    elif inter.geom_type == "Point":
        ys = [inter.y]
    elif inter.geom_type in ("MultiLineString", "LineString"):
        if hasattr(inter, "geoms"):
            for geom in inter.geoms:
                ys.extend([pt[1] for pt in geom.coords])
        else:
            ys = [pt[1] for pt in inter.coords]
    else:
        ys = [pt[1] for pt in inter.coords]
    y_bot, y_top = min(ys), max(ys)
    h = (y_top - y_bot) * height_fraction
    y_c = (y_top + y_bot) / 2
    y_bot_new = y_c - h / 2
    y_top_new = y_c + h / 2
    poly = Polygon(
        [
            (x_c - thickness / 2, y_bot_new),
            (x_c + thickness / 2, y_bot_new),
            (x_c + thickness / 2, y_top_new),
            (x_c - thickness / 2, y_top_new),
        ]
    )
    return poly


def airfoil_with_thickness(coords, thickness=0.0):
    """
    Returns outer (Polygon), and inner (Polygon or None) for hollow shells.
    """
    from shapely.geometry import Polygon

    outer = Polygon(coords)
    if thickness <= 0:
        return outer, None
    inner = outer.buffer(-thickness, join_style=2)
    if inner.is_empty or not inner.is_valid:
        raise ValueError("Thickness too large for airfoil.")
    if inner.geom_type == "MultiPolygon":
        inner = max(inner.geoms, key=lambda p: p.area)
    return outer, inner


def make_sectionproperties_geometry(outer, spars, holes=None, inner_shell=None):
    """
    outer: shapely Polygon (airfoil)
    spars: list of shapely Polygons (for each spar)
    holes: list of shapely Polygons (holes/cutouts)
    inner_shell: Polygon if present (for hollow shell airfoil)
    Returns: sectionproperties CompoundGeometry
    """
    # 1. Boolean: union all solids (airfoil + spars)
    solid = unary_union([outer] + spars)
    region = solid
    if holes is not None:
        # 2. Boolean: difference all holes (including inner shell if present)
        all_holes = [h for h in holes]
        if inner_shell is not None:
            all_holes.append(inner_shell)
        if all_holes:
            region = solid.difference(unary_union(all_holes))
        else:
            region = solid

    # Handle MultiPolygon result (e.g. if some spar is not connected)
    if region.geom_type == "MultiPolygon":
        solids = list(region.geoms)
    else:
        solids = [region]

    # For each exterior region: extract points/facets, 1 control point
    points = []
    facets = []
    control_points = []
    holes_pts = []

    idx_offset = 0
    for solid in solids:
        coords = list(solid.exterior.coords)
        n = len(coords)
        points.extend(coords)
        facets += [(idx_offset + i, idx_offset + i + 1) for i in range(n - 1)]
        cp = solid.representative_point().coords[0]
        control_points.append(cp)
        # Now handle holes in this solid
        for hole in solid.interiors:
            hole_coords = list(hole.coords)
            n2 = len(hole_coords)
            points.extend(hole_coords)
            facets += [
                (idx_offset + n + i, idx_offset + n + i + 1) for i in range(n2 - 1)
            ]
            hp = Polygon(hole_coords).representative_point().coords[0]
            holes_pts.append(hp)
            idx_offset += n2
        idx_offset += n

    return CompoundGeometry.from_points(
        points=points,
        facets=facets,
        control_points=control_points,
        holes=holes_pts if holes_pts else None,
    )
