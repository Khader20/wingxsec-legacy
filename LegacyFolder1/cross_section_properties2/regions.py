# cross_section_properties/regions.py

from .helpers import ensure_closed, get_interior_point
import numpy as np
from .helpers import ensure_closed, get_interior_point
from shapely.geometry import Polygon as ShapelyPolygon, LineString


class AirfoilRegion:
    """
    Airfoil solid or shell (with or without void).
    """

    def __init__(self, coords, skin_thickness=0, label="airfoil", material=None):
        from .airfoil import airfoil_with_thickness

        shells = airfoil_with_thickness(coords, skin_thickness)
        self.label = label
        self.material = material
        self.solid_coords = shells[0]
        self.hole_coords = shells[1] if len(shells) > 1 else None

    def get_points_and_facets(self):
        pts = []
        facets = []
        # Outer
        outer = ensure_closed(self.solid_coords)
        n = len(outer)
        pts.extend(outer)
        facets += [(i, i + 1) for i in range(n - 1)]
        # Inner (hole)
        if self.hole_coords is not None:
            hole = ensure_closed(self.hole_coords)
            n2 = len(hole)
            pts.extend(hole)
            facets += [(len(outer) + i, len(outer) + i + 1) for i in range(n2 - 1)]
        return pts, facets

    def get_control_point(self):
        return get_interior_point(self.solid_coords)

    def get_hole_point(self):
        if self.hole_coords is not None:
            return get_interior_point(self.hole_coords)
        return None


class RobustSparRegion:
    """
    Adds a vertical spar at x_c. Height is found by airfoil intersection at x_c.
    """

    def __init__(
        self,
        airfoil_coords,
        x_c,
        thickness,
        material,
        height_fraction=1.0,
        label="spar",
    ):
        self.label = label
        self.material = material
        # Find intersection with airfoil
        poly = ShapelyPolygon(airfoil_coords)
        miny, maxy = poly.bounds[1], poly.bounds[3]
        # Make a long vertical line
        line = LineString([(x_c, miny - 1), (x_c, maxy + 1)])
        inter = poly.intersection(line)
        # Extract intersection y-coords
        if inter.is_empty:
            raise ValueError(
                f"Spar at x={x_c:.3f} does not intersect airfoil geometry."
            )
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
        # Rectangle points (counter-clockwise)
        self.rect = [
            (x_c - thickness / 2, y_bot_new),
            (x_c + thickness / 2, y_bot_new),
            (x_c + thickness / 2, y_top_new),
            (x_c - thickness / 2, y_top_new),
            (x_c - thickness / 2, y_bot_new),
        ]

    def get_points_and_facets(self):
        pts = self.rect
        facets = [(i, i + 1) for i in range(len(pts) - 1)]
        return pts, facets

    def get_control_point(self):
        xs, ys = zip(*self.rect)
        return (np.mean(xs), np.mean(ys))


class CutoutRegion:
    def __init__(self, coords, label="cutout"):
        self.label = label
        self.material = None
        self.coords = ensure_closed(coords)

    def get_points_and_facets(self):
        pts = self.coords
        facets = [(i, i + 1) for i in range(len(pts) - 1)]
        return pts, facets

    def get_control_point(self):
        return get_interior_point(self.coords)
