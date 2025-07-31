# from cross_section_properties.airfoil.generators import naca4_points
# from cross_section_properties.materials.material_db import aluminum
# from cross_section_properties.geometry.hollow import true_hollow_skin
# from sectionproperties.analysis.section import Section

# # Outer airfoil coordinates
# points = naca4_points('0015', chord=0.2, n_points=200)
# # Build "skin" geometry as a solid ring
# geom = true_hollow_skin(
#     outer_points=points,
#     skin_thickness=0.003,
#     material=aluminum()
# )

# geom.create_mesh(mesh_sizes=[0.0001])
# sec = Section(geometry=geom)
# sec.calculate_geometric_properties()
# sec.calculate_warping_properties()
# sec.calculate_plastic_properties()
# print("Area:", sec.get_area())
# print("Centroid (cx, cy):", sec.get_c())
# # print("Ix, Iy, Ixy:", sec.get_ic())
# sec.plot_mesh()
# sec.plot_centroids()


# from cross_section_properties.airfoil.generators import naca4_points
# from cross_section_properties.geometry.hollow import *
# from cross_section_properties.materials.material_db import aluminum, steel
# from sectionproperties.analysis.section import Section

# # Outer airfoil coordinates
# points = naca4_points('0012', chord=1.0, n_points=100)
# skin = true_hollow_skin(
#     outer_points=points,
#     skin_thickness=0.02,
#     material=aluminum()
# )

# # Add a spar at 30% chord, thickness 0.015, with steel
# compound = add_spar_to_airfoil_skin(
#     skin_geom=skin,
#     airfoil_pts=points,
#     x_spar=0.3,
#     t_spar=0.015,
#     mat_spar=steel()
# )

# compound.create_mesh(mesh_sizes=[0.001])
# sec = Section(geometry=compound)
# sec.calculate_geometric_properties()
# sec.calculate_warping_properties()
# sec.calculate_plastic_properties()
# print("Area:", sec.get_area())
# print("Centroid (cx, cy):", sec.get_c())
# sec.plot_mesh()
# sec.plot_centroids()


from cross_section_properties4.airfoil.generators import naca4_points
from cross_section_properties4.materials.material_db import aluminum, steel
from cross_section_properties4.geometry.airfoil_struct import AirfoilWithSpars
from sectionproperties.analysis.section import Section

points = naca4_points("0015", chord=1.0, n_points=100)
spars = [
    {"x_chord": 0.3, "thickness": 0.015, "material": steel()},
    {"x_chord": 0.7, "thickness": 0.010, "material": steel()},
]

builder = AirfoilWithSpars(
    outer_pts=points, skin_thickness=0.02, skin_material=aluminum(), spar_specs=spars
)

compound_geom = builder.build()
compound_geom.create_mesh(mesh_sizes=[0.10])
sec = Section(geometry=compound_geom)
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
sec.calculate_plastic_properties()
print("Area:", sec.get_area())
print("Centroid (cx, cy):", sec.get_c())
sec.plot_mesh()
sec.plot_centroids()
