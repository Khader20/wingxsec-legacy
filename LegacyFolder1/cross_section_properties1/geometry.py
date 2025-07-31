# cross_section_properties/geometry.py

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, LinearRing, LineString

from .material import Material


def airfoil_with_thickness(coords, thickness):
    """
    Returns outer and inner polygon coordinates for an airfoil wall of given thickness.
    If thickness=0, returns just the original.
    If thickness>0, returns both boundaries.
    """
    outer_poly = ShapelyPolygon(coords)
    if thickness == 0:
        return coords, None
    inner_poly = outer_poly.buffer(-thickness, join_style=2)
    if inner_poly.is_empty:
        raise ValueError("Thickness too large: inner polygon disappeared.")
    inner_coords = np.array(inner_poly.exterior.coords)
    return coords, inner_coords


class CrossSectionGeometry:
    """
    Composite cross-section geometry builder for FE analysis.
    """

    def __init__(self):
        self.regions = (
            []
        )  # [{'polygon': ..., 'material': ..., 'label': ..., 'type': ...}]
        self.cutouts = []

    def add_airfoil(
        self,
        airfoil_coords: np.ndarray,
        skin_thickness: float,
        material: Material,
        label: str = "skin",
    ):
        """
        Adds an airfoil region:
          - skin_thickness == 0: The airfoil is filled (solid region)
          - skin_thickness > 0: Hollow shell (true hole, white in preview)
        """
        airfoil_coords = np.asarray(airfoil_coords)
        if not np.allclose(airfoil_coords[0], airfoil_coords[-1]):
            airfoil_coords = np.vstack([airfoil_coords, airfoil_coords[0]])
        outer_coords, inner_coords = airfoil_with_thickness(
            airfoil_coords, skin_thickness
        )
        if skin_thickness == 0 or inner_coords is None:
            poly = ShapelyPolygon(outer_coords)
            region_type = "filled"
        else:
            poly = ShapelyPolygon(outer_coords, [inner_coords])
            region_type = "skin"
        self.regions.append(
            {"polygon": poly, "material": material, "label": label, "type": region_type}
        )

    def add_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        material: Material,
        label: str = "rect",
    ):
        poly = ShapelyPolygon(
            [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        )
        self.regions.append(
            {"polygon": poly, "material": material, "label": label, "type": "filled"}
        )

    def add_spar(
        self,
        x_c: float,
        thickness: float,
        material: Material,
        height_fraction: float = 1.0,
        label: str = "spar",
    ):
        """
        Adds a vertical spar at chordwise position x_c. Height is matched to the airfoil depth at that x.
        """
        if not self.regions:
            raise RuntimeError("Add airfoil first before adding spars.")
        airfoil_poly = self.regions[0]["polygon"]
        bounds = airfoil_poly.bounds
        line = LineString([(x_c, bounds[1] - 1.0), (x_c, bounds[3] + 1.0)])
        inter = airfoil_poly.intersection(line)
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
        poly = ShapelyPolygon(
            [
                (x_c - thickness / 2, y_bot_new),
                (x_c + thickness / 2, y_bot_new),
                (x_c + thickness / 2, y_top_new),
                (x_c - thickness / 2, y_top_new),
            ]
        )
        self.regions.append(
            {"polygon": poly, "material": material, "label": label, "type": "filled"}
        )

    def add_cutout(self, polygon_coords: np.ndarray, label: str = "cutout"):
        poly = ShapelyPolygon(polygon_coords)
        self.cutouts.append(poly)

    def get_shapely_polygons(self):
        """
        Returns all polygons with materials, subtracting cutouts.
        """
        all_regions = []
        for region in self.regions:
            poly = region["polygon"]
            for cutout in self.cutouts:
                poly = poly.difference(cutout)
            all_regions.append(
                (
                    poly,
                    region["material"],
                    region["label"],
                    region.get("type", "filled"),
                )
            )
        return all_regions

    def preview(self, show_labels: bool = True):
        """
        Visualizes the cross-section with all regions colored by material, holes and cutouts always white.
        Plots directly to the main plt window for better aspect and scaling.
        """
        plt.figure(figsize=(10, 6))
        ax = plt.gca()

        for i, (poly, mat, label, region_type) in enumerate(
            self.get_shapely_polygons()
        ):
            if poly.is_empty:
                continue
            # Draw exterior
            x, y = poly.exterior.xy
            ax.fill(
                x,
                y,
                color=mat.color,
                alpha=1.0,
                label=f"{label} [{mat.name}]" if i == 0 else "",
            )
            # Draw holes as white
            for hole in poly.interiors:
                hx, hy = hole.xy
                ax.fill(hx, hy, color="white", alpha=1.0)
            if show_labels:
                xc, yc = poly.centroid.xy
                ax.text(
                    float(xc[0]),
                    float(yc[0]),
                    f"{label}",
                    fontsize=9,
                    ha="center",
                    va="center",
                )
        # Cutouts in white
        for i, cutout in enumerate(self.cutouts):
            if not cutout.is_empty:
                x, y = cutout.exterior.xy
                ax.fill(
                    x,
                    y,
                    color="white",
                    alpha=1.0,
                    label="cutout" if i == 0 else None,
                    hatch="//",
                )

        ax.axis("equal")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.set_title("Cross-Section Geometry Preview")
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc="best")
        plt.tight_layout()
        plt.show()


# # ===== Example Usage =====
# if __name__ == "__main__":
#     from .material import Material
#     from .airfoil_library import AirfoilLibrary

#     mat_skin = Material('CFRP', 70e9, 5e9, 1600, 0.3, '#2ca02c')
#     chord = 1.0
#     airfoil_coords = AirfoilLibrary.naca_4_series('0015', chord=chord, n_points=200)

#     geom = CrossSectionGeometry()
#     # Hollow shell (skin)
#     geom.add_airfoil(airfoil_coords, skin_thickness=0.004, material=mat_skin, label='skin')
#     # Add a cutout example
#     # t = np.linspace(0, 2 * np.pi, 100)
#     # cutout_coords = np.column_stack([0.5 + 0.03 * np.cos(t), 0.01 + 0.01 * np.sin(t)])
#     # geom.add_cutout(cutout_coords)
#     geom.preview()
