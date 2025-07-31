# cross_section_properties/compute.py

import numpy as np
from sectionproperties.pre.geometry import Polygon as SP_Polygon
from sectionproperties.pre.pre import Material as SP_Material
from sectionproperties.analysis.section import Section


def ensure_closed(coords):
    """Returns a closed list of (float, float) tuples, as required by sectionproperties."""
    coords = np.array(coords)
    if coords.shape[0] == 0:
        return []
    if not np.allclose(coords[0], coords[-1]):
        coords = np.vstack([coords, coords[0]])
    return [(float(pt[0]), float(pt[1])) for pt in coords]


class CrossSection:
    """
    Professional interface to sectionproperties for arbitrary composite cross-sections.
    """

    def __init__(self, geometry, mesh_size=0.001):
        """
        :param geometry: CrossSectionGeometry instance (from geometry.py)
        :param mesh_size: Default mesh size (in meters)
        """
        self.geometry = geometry
        self.mesh_size = mesh_size
        self._geometry = None  # sectionproperties Geometry object (after build)
        self.sp_section = None  # sectionproperties Section object (after mesh & build)
        self._results = None  # Results dictionary after compute_properties()

    def build_section(self):
        """
        Converts all regions to sectionproperties Polygons, combines, meshes, and builds the Section.
        """
        geom = None
        for poly, mat, label, region_type in self.geometry.get_shapely_polygons():
            if poly.is_empty:
                continue
            shell = ensure_closed(poly.exterior.coords)
            holes = (
                [ensure_closed(hole.coords) for hole in poly.interiors]
                if poly.interiors
                else None
            )
            # sectionproperties Material object
            spmat = SP_Material(
                name=mat.name,
                elastic_modulus=mat.E,
                poissons_ratio=mat.nu,
                density=mat.density,
                yield_strength=1e9,
                color=mat.color,
            )
            region_poly = SP_Polygon(shell, holes=holes, material=spmat)
            geom = region_poly if geom is None else geom + region_poly

        if geom is None:
            raise RuntimeError("No valid regions to build Section.")

        # Only now create the mesh (before Section!)
        geom.create_mesh(mesh_sizes=self.mesh_size)
        self._geometry = geom

        # Section construction (no mesh here, must be pre-meshed)
        self.sp_section = Section(geom)

    def compute_properties(self):
        """
        Runs sectionproperties analysis and stores key section properties.
        """
        if self.sp_section is None:
            raise RuntimeError("Call build_section() before compute_properties().")
        section = self.sp_section

        section.calculate_geometric_properties()
        section.calculate_warping_properties()
        section.calculate_plastic_properties()

        props = section.get_results()
        self._results = {
            "area": props.get("area"),
            "cx": props.get("cx"),
            "cy": props.get("cy"),
            "Ixx_c": props.get("Ixx_c"),
            "Iyy_c": props.get("Iyy_c"),
            "Ixy_c": props.get("Ixy_c"),
            "J": props.get("j"),
            "sc_x": props.get("scx"),
            "sc_y": props.get("scy"),
            "gamma_max": props.get("gamma_max"),
            "phi_m_max": props.get("phi_m_max"),
            "A_sx": props.get("asx"),
            "A_sy": props.get("asy"),
            "mass": props.get("mass"),
        }

    def get_results(self):
        """
        Returns a dictionary of computed section properties.
        """
        if self._results is None:
            raise RuntimeError("No results: Run compute_properties() first.")
        return self._results

    def plot_results(self, plot_type="geometry"):
        """
        Plots geometry, mesh, or stress using sectionproperties.
        plot_type: 'geometry', 'mesh', 'stress', 'warp', etc.
        """
        if self.sp_section is None:
            raise RuntimeError("Call build_section() before plotting.")
        import matplotlib.pyplot as plt

        section = self.sp_section
        if plot_type == "geometry":
            section.plot_geometry()
        elif plot_type == "mesh":
            section.plot_mesh()
        elif plot_type == "stress":
            section.plot_stress(stress="mises")
        elif plot_type == "warp":
            section.plot_warping()
        else:
            raise ValueError(
                "Unknown plot_type. Use 'geometry', 'mesh', 'stress', or 'warp'."
            )
        plt.show()


# # ===== Example Usage =====
# if __name__ == "__main__":
#     from cross_section_properties.geometry import CrossSectionGeometry
#     from cross_section_properties.material import Material
#     from cross_section_properties.airfoil_library import AirfoilLibrary

#     mat_skin = Material("CFRP", 70e9, 5e9, 1600, 0.3, "#2ca02c")
#     chord = 1.0
#     airfoil_coords = AirfoilLibrary.naca_4_series("0015", chord=chord, n_points=200)

#     geom = CrossSectionGeometry()
#     geom.add_airfoil(
#         airfoil_coords, skin_thickness=0.004, material=mat_skin, label="skin"
#     )

#     section = CrossSection(geom, mesh_size=0.002)
#     section.build_section()
#     section.compute_properties()
#     results = section.get_results()
#     print("Area:", results["area"])
#     print("Centroid (cx, cy):", results["cx"], results["cy"])
#     print("Ixx, Iyy, Ixy:", results["Ixx_c"], results["Iyy_c"], results["Ixy_c"])
#     print("J (torsion):", results["J"])
#     print("Shear center (x, y):", results["sc_x"], results["sc_y"])

#     section.plot_results("geometry")
#     section.plot_results("mesh")
