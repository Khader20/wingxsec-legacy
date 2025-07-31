import numpy as np
from shapely.geometry import Polygon, LineString
from sectionproperties.pre import Material, CompoundGeometry
from airfoil import airfoil_with_thickness


class SectionBuilder:
    def __init__(self):
        self.regions = []

    def add_airfoil(self, coords, skin_thickness=0.0, material=None, label="airfoil"):
        """
        Adds airfoil as a filled or hollow region (shell).
        """
        outer, inner = airfoil_with_thickness(coords, skin_thickness)
        # Outer always added (filled or shell)
        self.regions.append(
            {"polygon": outer, "material": material, "is_void": False, "label": label}
        )
        # If hollow: add void (inner) region as well
        if inner is not None:
            self.regions.append(
                {
                    "polygon": inner,
                    "material": None,
                    "is_void": True,
                    "label": f"{label}_void",
                }
            )

    def add_spar(self, x_c, thickness, material, height_fraction=1.0, label="spar"):
        """
        Add a vertical spar at chordwise position x_c. Height auto-detected from airfoil!
        """
        if not self.regions:
            raise RuntimeError("Add airfoil first before adding spars.")
        airfoil_poly = self.regions[0]["polygon"]
        bounds = airfoil_poly.bounds
        # Draw a vertical line through the airfoil at x_c (extend far enough)
        test_line = LineString([(x_c, bounds[1] - 1.0), (x_c, bounds[3] + 1.0)])
        inter = airfoil_poly.intersection(test_line)
        # Find min/max y at intersection points
        if inter.is_empty:
            raise ValueError(
                f"Spar at x={x_c:.3f} does not intersect airfoil geometry."
            )
        if inter.geom_type == "MultiPoint":
            pts = sorted(inter.geoms, key=lambda pt: pt.y)
            y_bot, y_top = pts[0].y, pts[-1].y
        elif inter.geom_type == "Point":
            y_bot = y_top = inter.y
        elif inter.geom_type == "MultiLineString":
            ys = [pt for line in inter.geoms for pt in line.coords]
            ys = [p[1] for p in ys]
            y_bot, y_top = min(ys), max(ys)
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
        self.regions.append(
            {"polygon": poly, "material": material, "is_void": False, "label": label}
        )

    def to_compound(self):
        """
        Converts all regions to CompoundGeometry (as per sectionproperties).
        """
        points = []
        facets = []
        control_points = []
        holes = []
        materials = []
        idx_offset = 0
        for reg in self.regions:
            poly = reg["polygon"]
            coords = list(poly.exterior.coords)
            n = len(coords)
            points.extend(coords)
            facets.extend([(idx_offset + i, idx_offset + i + 1) for i in range(n - 1)])
            # For each region, pick a guaranteed interior point
            pt = poly.representative_point().coords[0]
            if reg["is_void"]:
                holes.append(pt)
            else:
                control_points.append(pt)
                materials.append(reg["material"])
            idx_offset += n
        # sectionproperties expects at least one control point for each solid region!
        from sectionproperties.pre import CompoundGeometry

        return CompoundGeometry.from_points(
            points=points,
            facets=facets,
            control_points=control_points,
            holes=holes if holes else None,
            materials=materials if materials else None,
        )

    def preview(self, ax=None):
        """
        Quick preview using matplotlib (filled=gray, void=white, spar=blue).
        """
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MplPoly

        if ax is None:
            fig, ax = plt.subplots()
        for reg in self.regions:
            poly = reg["polygon"]
            is_void = reg["is_void"]
            color = (
                "white"
                if is_void
                else "#bbbbbb" if "airfoil" in reg["label"] else "#2c5cbe"
            )
            mpl_poly = MplPoly(
                np.asarray(poly.exterior.coords),
                facecolor=color,
                edgecolor="k",
                alpha=0.7,
            )
            ax.add_patch(mpl_poly)
        ax.axis("equal")
        ax.autoscale()
        plt.show()
