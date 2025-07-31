# cross_section_properties/geometry/airfoil_struct.py

from typing import List, Tuple
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from sectionproperties.pre.geometry import Geometry, CompoundGeometry
from ..geometry.hollow import offset_polygon


class AirfoilSkin:
    """
    Represents a hollow airfoil skin (polygonal ring).
    """

    def __init__(
        self,
        outer_pts: List[Tuple[float, float]],
        skin_thickness: float,
        material,
        control_point=(0.5, 0.0),
    ):

        inner_pts = offset_polygon(outer_pts, skin_thickness)
        # Skin polygon: outer CCW + inner CW
        self.outer_pts = outer_pts
        self.inner_pts = inner_pts[::-1]  # reverse for CW
        self.material = material
        self.control_point = control_point

    def as_shapely(self) -> Polygon:
        return Polygon(self.outer_pts, [self.inner_pts])

    def section_geom(self) -> Geometry:
        # Build a single region polygon for the skin (no overlaps)
        skin_poly = self.as_shapely()
        skin_pts = list(skin_poly.exterior.coords)[:-1] + [
            tuple(p)
            for ring in skin_poly.interiors
            for p in list(ring.coords)[:-1][::-1]
        ]
        # Facets for both outer and inner
        n_outer = len(self.outer_pts)
        n_inner = len(self.inner_pts)
        facets = [(i, i + 1) for i in range(n_outer - 1)] + [(n_outer - 1, 0)]
        facets += [(n_outer + i, n_outer + i + 1) for i in range(n_inner - 1)] + [
            (n_outer + n_inner - 1, n_outer)
        ]
        return Geometry.from_points(
            points=skin_pts,
            facets=facets,
            control_points=[self.control_point],
            material=self.material,
        )


class AirfoilWithSpars:
    """
    Build a hollow airfoil with one or more spars, ensuring no overlap.
    """

    def __init__(
        self,
        outer_pts: List[Tuple[float, float]],
        skin_thickness: float,
        skin_material,
        spar_specs: List[dict],
        skin_control_point=(0.5, 0.0),
    ):
        """
        spar_specs: list of dicts, each with:
            - x_chord: chordwise position (0-1)
            - thickness: spar thickness
            - material: spar material
        """
        self.outer_pts = outer_pts
        self.skin_thickness = skin_thickness
        self.skin_material = skin_material
        self.spar_specs = spar_specs
        self.skin_control_point = skin_control_point

    def build(self) -> CompoundGeometry:
        # 1. Create skin as shapely polygon
        skin = AirfoilSkin(
            self.outer_pts,
            self.skin_thickness,
            self.skin_material,
            self.skin_control_point,
        )
        skin_poly = skin.as_shapely()

        spar_geoms = []
        cutouts = []
        for spar in self.spar_specs:
            x_spar = spar["x_chord"]
            t_spar = spar["thickness"]
            material = spar["material"]
            # Find top/bottom intersections
            from ..geometry.airfoil_struct import (
                find_spar_intersection,
            )

            y_bot, y_top = find_spar_intersection(self.outer_pts, x_spar)
            # Spar rectangle
            x0 = x_spar - t_spar / 2
            x1 = x_spar + t_spar / 2
            spar_poly = box(x0, y_bot, x1, y_top)
            cutouts.append(spar_poly)
            # Center control point
            spar_cp = [(x_spar, (y_bot + y_top) / 2)]
            # Get spar as points/facets
            spar_pts = [(x0, y_bot), (x1, y_bot), (x1, y_top), (x0, y_top)]
            spar_facets = [(i, i + 1) for i in range(3)] + [(3, 0)]
            spar_geoms.append(
                Geometry.from_points(spar_pts, spar_facets, spar_cp, material=material)
            )

        # 2. Subtract all spar cutouts from the skin polygon (no overlap)
        skin_cut = skin_poly
        if cutouts:
            skin_cut = skin_poly.difference(unary_union(cutouts))

        # 3. Build skin Geometry
        skin_regions = []
        if skin_cut.geom_type == "Polygon":
            polys = [skin_cut]
        else:
            polys = list(skin_cut.geoms)
        for poly in polys:
            # Outer (CCW), inner holes (CW)
            ext = list(poly.exterior.coords)[:-1]
            ints = [list(hole.coords)[:-1][::-1] for hole in poly.interiors]
            pts = ext + [p for ring in ints for p in ring]
            n_outer = len(ext)
            n_inner = sum([len(ring) for ring in ints])
            facets = [(i, i + 1) for i in range(n_outer - 1)] + [(n_outer - 1, 0)]
            offset = n_outer
            for ring in ints:
                facets += [
                    (offset + i, offset + i + 1) for i in range(len(ring) - 1)
                ] + [(offset + len(ring) - 1, offset)]
                offset += len(ring)
            skin_regions.append(
                Geometry.from_points(
                    pts, facets, [self.skin_control_point], material=self.skin_material
                )
            )

        # 4. Compound
        all_geoms = skin_regions + spar_geoms
        return CompoundGeometry(all_geoms)


# Helper: intersection search (as above)
def find_spar_intersection(airfoil_pts, x_spar):
    from shapely.geometry import LineString, Polygon

    airfoil_poly = Polygon(airfoil_pts)
    spar_line = LineString([(x_spar, -10), (x_spar, 10)])
    intersections = airfoil_poly.boundary.intersection(spar_line)
    if intersections.is_empty:
        raise ValueError("Spar does not intersect airfoil at this chordwise location.")
    if intersections.geom_type == "MultiPoint":
        ys = [p.y for p in intersections.geoms]
    else:
        ys = [intersections.y]
    ys = sorted(ys)
    if len(ys) < 2:
        raise ValueError("Vertical at x_spar did not intersect airfoil in two places.")
    return ys[0], ys[-1]
