from rich import print
import numpy as np
import os

from cross_section_properties1.material import *
from cross_section_properties1.airfoil_library import *
from cross_section_properties1.geometry import *
from cross_section_properties1.compute import *

# # ===== Example Usage =====
# if __name__ == "__main__":
#     # Example materials
#     CFRP = Material("CFRP", E=70e9, G=5e9, density=1600, nu=0.3, color="#2ca02c")
#     AL = Material("Aluminum", E=70e9, G=26e9, density=2700, nu=0.33, color="#1f77b4")
#     print(CFRP)
#     print(AL)




# # ===== Example Usage =====
# if __name__ == "__main__":
#     # Generate NACA 0015 coordinates
#     coords = AirfoilLibrary.naca_4_series('0015', chord=0.3, n_points=200)
#     import matplotlib.pyplot as plt
#     plt.figure(figsize=(10,6))
#     plt.plot(coords[:, 0], coords[:, 1], color='orange', label="NACA 0015")
#     plt.scatter(coords[:, 0], coords[:, 1], c='k', marker='.', s=10)
#     plt.axis('equal'); plt.grid(True); plt.legend(); plt.title(f"NACA 0015 Airfoil | total # points = {len(coords)+1}"); plt.show()

#     # Example loading .dat (if you have data/NACA0012.dat, etc.)

#     current_file_dir = os.path.dirname(os.path.abspath(__file__))
#     project_root_dir = os.path.abspath(os.path.join(current_file_dir, '.'))
#     data_file_path = os.path.join(project_root_dir, "cross_section_properties1/data", "naca0015.dat")

#     coords2 = AirfoilLibrary.load_from_dat(data_file_path, chord=0.3, n_points=200)
#     plt.figure(figsize=(10,6))
#     plt.plot(coords2[:, 0], coords2[:, 1], color='blue' ,label="naca0015.dat")
#     plt.scatter(coords2[:, 0], coords2[:, 1], c='k', marker='.', s=10)
#     plt.axis('equal'); plt.grid(True); plt.legend(); plt.title(f"naca0015.dat Airfoil | total # points = {len(coords2)+1}"); plt.show()

#     print("[bold green]Finished AirfoilLibrary examples.[/bold green]")






# ===== Example Usage =====
# if __name__ == "__main__":
    # # 1. Materials
    # mat_skin = Material('CFRP', 70e9, 5e9, 1600, 0.3, '#2ca02c')
    # mat_spar = Material('Al', 70e9, 26e9, 2700, 0.33, '#1f77b4')

    # # 2. Geometry
    # geom = CrossSectionGeometry()

    # # Airfoil (NACA0015)
    # airfoil_coords = AirfoilLibrary.naca_4_series('0015', chord=0.3, n_points=200)
    # # Filled (solid) airfoil:
    # geom.add_airfoil(airfoil_coords, skin_thickness=0, material=mat_skin)
    # # Hollow shell (e.g., real structure):
    # geom.add_airfoil(airfoil_coords, skin_thickness=0.003, material=mat_skin)


    # # Spars
    # # geom.add_spar(x_c=0.3*0.25, thickness=0.003, material=mat_spar)  # Full-depth spar, auto-placed
    # # geom.add_spar(0.3, 0.3, width=0.04, thickness=0.015, material=mat_spar, label='front spar')
    # # geom.add_spar(0.7, 0.7, width=0.04, thickness=0.004, material=mat_spar, label='rear spar')

    # # Example cutout (ellipse for inspection hole)
    # t = np.linspace(0, 2*np.pi, 100)
    # x_c, y_c, a, b = 0.5, 0.02, 0.03, 0.01
    # cutout = np.column_stack([x_c + a*np.cos(t), y_c + b*np.sin(t)])
    # geom.add_cutout(cutout)

    # # preview
    # geom.preview()








    # mat_skin = Material('CFRP', 70e9, 5e9, 1600, 0.3, '#2ca02c')
    # chord = 1
    # airfoil_coords = AirfoilLibrary.naca_4_series('0015', chord=chord, n_points=200)

    # geom = CrossSectionGeometry()
    # # Filled airfoil (solid)
    # # geom.add_airfoil(airfoil_coords, skin_thickness=0, material=mat_skin, label='filled')
    # # Hollow shell (skin)
    # geom.add_airfoil(airfoil_coords, skin_thickness=0.004, material=mat_skin, label='skin')
    # geom.preview()





    # mat_skin = Material('CFRP', 70e9, 5e9, 1600, 0.3, "#1c8ee6")
    # mat_spar = Material('Al', 70e9, 26e9, 2700, 0.33, "#ef670c")

    # chord = 0.3
    # airfoil_coords = AirfoilLibrary.naca_4_series('0015', chord=chord, n_points=200)

    # geom = CrossSectionGeometry()
    # # Hollow shell (skin)
    # geom.add_airfoil(airfoil_coords, skin_thickness=0.003, material=mat_skin, label='skin')
    # # Add a cutout example
    # # t = np.linspace(0, 2 * np.pi, 100)
    # # cutout_coords = np.column_stack([0.5 + 0.03 * np.cos(t), 0.01 + 0.01 * np.sin(t)])
    # # geom.add_cutout(cutout_coords)

    # # Spars
    # geom.add_spar(x_c=0.3*0.25, thickness=0.003, material=mat_spar)  # Full-depth spar, auto-placed


    # geom.preview()




# # ===== Example Usage =====
# if __name__ == "__main__":
#     mat_skin = Material('CFRP', 70e9, 5e9, 1600, 0.3, '#2ca02c')
#     chord = 1.0
#     airfoil_coords = AirfoilLibrary.naca_4_series('0015', chord=chord, n_points=200)

#     geom = CrossSectionGeometry()
#     geom.add_airfoil(airfoil_coords, skin_thickness=0.004, material=mat_skin, label='skin')

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






# from sectionproperties.analysis import Section
# from sectionproperties.pre import CompoundGeometry

# w_a = 1  # width of angle leg
# w_p = 2  # width of bottom plate
# d = 2  # depth of section
# t = 0.1  # thickness of section

# # list of points describing the geometry
# points = [
#     (w_p * -0.5, 0),  # bottom plate
#     (w_p * 0.5, 0),
#     (w_p * 0.5, t),
#     (w_p * -0.5, t),
#     (t * -0.5, t),  # inverted angle section
#     (t * 0.5, t),
#     (t * 0.5, d - t),
#     (w_a - 0.5 * t, d - t),
#     (w_a - 0.5 * t, d),
#     (t * -0.5, d),
# ]

# # list of facets (edges) describing the geometry connectivity
# facets = [
#     (0, 1),  # bottom plate
#     (1, 2),
#     (2, 3),
#     (3, 0),
#     (4, 5),  # inverted angle section
#     (5, 6),
#     (6, 7),
#     (7, 8),
#     (8, 9),
#     (9, 4),
# ]

# # list of control points (points within each region)
# control_points = [
#     (0, t * 0.5),  # bottom plate
#     (0, d - t),  # inverted angle section
# ]

# geom = CompoundGeometry.from_points(
#     points=points,
#     facets=facets,
#     control_points=control_points,
# )
# geom.plot_geometry()


# geom.create_mesh(mesh_sizes=[0.0005, 0.001])

# sec = Section(geometry=geom)
# sec.plot_mesh(materials=False)

# sec.calculate_geometric_properties()
# # sec.calculate_warping_properties()
# # sec.calculate_plastic_properties()

# sec.plot_centroids()

# sec.display_results()



















from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry

w_a = 1  # width of angle leg
w_p = 2  # width of bottom plate
d = 2  # depth of section
t = 0.1  # thickness of section

# list of points describing the geometry
points = [
    (w_p * -0.5, 0),  # bottom plate
    (w_p * 0.5, 0),
    (w_p * 0.5, t),
    (w_p * -0.5, t),
    (t * -0.5, t),  # inverted angle section
    (t * 0.5, t),
    (t * 0.5, d - t),
    (w_a - 0.5 * t, d - t),
    (w_a - 0.5 * t, d),
    (t * -0.5, d),
]

# list of facets (edges) describing the geometry connectivity
facets = [
    (0, 1),  # bottom plate
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),  # inverted angle section
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 4),
]

# list of control points (points within each region)
control_points = [
    (0, t * 0.5),  # bottom plate
    (0, d - t),  # inverted angle section
]

geom = CompoundGeometry.from_points(points, facets, control_points)
geom.plot_geometry()         # Plot cross-section outline

# 2. Mesh
geom.create_mesh(mesh_sizes=2.0)
sec = Section(geometry=geom)
sec.plot_mesh()

# 3. Analysis
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
sec.calculate_plastic_properties()

# 4. Results
sec.display_results()
print(f"Area = {sec.get_area():.2f} mm²")
print(f"Centroid: {sec.get_c()}")
print(f"Ixx = {sec.get_ic()[0]:.3e} mm⁴")
print(f"Principal axis angle = {sec.get_phi():.2f} deg")
print(f"Torsion constant J = {sec.get_j():.3e} mm⁴")

sec.plot_centroids()
