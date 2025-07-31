from rich import print
import numpy as np
import os

# import sectionproperties.pre.library as spl
# from sectionproperties.analysis.section import Section

# d, b, tw, tf, r, n_r = 12, 50, 6, 3, 0, 0
# ibeam_geom = spl.i_section(d=d, b=b, t_f=tf, t_w=tw, r=r, n_r=n_r)
# ibeam_geom.create_mesh(mesh_sizes=[1])
# sec = Section(geometry=ibeam_geom)

# sec.calculate_geometric_properties()
# sec.calculate_warping_properties()
# sec.calculate_plastic_properties()

# print("Area:", sec.get_area())
# print("Centroid (cx, cy):", sec.get_c())
# print("Moments of inertia about centroid (ixx, iyy, ixy):", sec.get_ic())
# print("Torsion constant J:", sec.get_j())
# print("Shear centre Gamma:", sec.get_gamma())

# # Plastic modulus as a tuple (Zx, Zy)
# z = sec.get_z()
# print("Plastic modulus (Zx, Zy):", z)


# # Plot mesh
# sec.plot_mesh()

# # Plot centroid (geometric, elastic, and plastic)
# sec.plot_centroids()










# import sectionproperties.pre as sp_pre
# from sectionproperties.pre.geometry import Geometry, CompoundGeometry
# from sectionproperties.analysis.section import Section

# mat_flange = sp_pre.Material(
#     name="Steel Flange",
#     elastic_modulus=210e3,
#     poissons_ratio=0.3,
#     yield_strength=250,
#     density=7850,
#     color="grey"
# )
# mat_web = sp_pre.Material(
#     name="Concrete Web",
#     elastic_modulus=30e3,
#     poissons_ratio=0.2,
#     yield_strength=40,
#     density=2400,
#     color="orange"
# )

# d = 300
# b = 150
# tw = 10
# tf = 16

# # Top flange
# flange_top_pts = [(0, d - tf), (b, d - tf), (b, d), (0, d)]
# flange_top_facets = [(0, 1), (1, 2), (2, 3), (3, 0)]
# flange_top_cp = [(b / 2, d - tf / 2)]
# flange_top = Geometry.from_points(flange_top_pts, flange_top_facets, flange_top_cp, material=mat_flange)

# # Bottom flange
# flange_bot_pts = [(0, 0), (b, 0), (b, tf), (0, tf)]
# flange_bot_facets = [(0, 1), (1, 2), (2, 3), (3, 0)]
# flange_bot_cp = [(b / 2, tf / 2)]
# flange_bot = Geometry.from_points(flange_bot_pts, flange_bot_facets, flange_bot_cp, material=mat_flange)

# # Web
# web_x0 = b / 2 - tw / 2
# web_x1 = b / 2 + tw / 2
# web_pts = [(web_x0, tf), (web_x1, tf), (web_x1, d - tf), (web_x0, d - tf)]
# web_facets = [(0, 1), (1, 2), (2, 3), (3, 0)]
# web_cp = [(b / 2, d / 2)]
# web = Geometry.from_points(web_pts, web_facets, web_cp, material=mat_web)

# compound_geom = CompoundGeometry([flange_top, flange_bot, web])
# compound_geom.create_mesh(mesh_sizes=[8])

# sec = Section(geometry=compound_geom)
# sec.calculate_geometric_properties()
# sec.calculate_warping_properties()
# sec.calculate_plastic_properties()

# # print("Area:", sec.get_area())
# # print("Centroid (cx, cy):", sec.get_c())
# # print("Moments of inertia about centroid (ixx, iyy, ixy):", sec.get_ic())
# # print("Torsion constant J:", sec.get_j())
# # print("Shear centre Gamma:", sec.get_gamma())
# # print("Plastic modulus (Zx, Zy):", sec.get_z())

# sec.plot_mesh()
# sec.plot_centroids()
















import numpy as np

def naca4_coords(m: int, p: int, t: int, c: float = 1.0, n: int = 100):
    """
    Generate NACA 4-digit airfoil coordinates.
    m: max camber (% of chord) * 100
    p: location of max camber (% of chord) * 10
    t: thickness (% of chord) * 100
    c: chord length
    n: number of coordinate points per surface
    """
    m, p, t = m / 100.0, p / 10.0, t / 100.0
    x = np.linspace(0, c, n)
    yt = 5 * t * c * (
        0.2969 * np.sqrt(x / c) -
        0.1260 * (x / c) -
        0.3516 * (x / c)**2 +
        0.2843 * (x / c)**3 -
        0.1015 * (x / c)**4
    )
    if m == 0 and p == 0:
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
    else:
        yc = np.where(x < p * c,
                      m * x / (p**2) * (2 * p - x / c),
                      m * (c - x) / ((1 - p)**2) * (1 + x / c - 2 * p))
        dyc_dx = np.where(x < p * c,
                          2 * m / (p**2) * (p - x / c),
                          2 * m / ((1 - p)**2) * (p - x / c))
    theta = np.arctan(dyc_dx)

    # Upper surface
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    # Lower surface
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    # Combine coordinates
    coords = np.vstack([
        np.stack([xu, yu], axis=1),
        np.stack([xl[::-1], yl[::-1]], axis=1)[1:]
    ])
    return coords.tolist()




from sectionproperties.pre.geometry import Geometry
import sectionproperties.pre as sp_pre

# Generate NACA0012 (m=0, p=0, t=12) with chord 1.0 and 100 pts per surface
airfoil_pts = naca4_coords(0, 0, 12, c=1.0, n=100)

# Define facets (just connect consecutive points)
facets = [(i, i+1) for i in range(len(airfoil_pts)-1)]
facets.append((len(airfoil_pts)-1, 0))  # close the loop

# At least one control point inside the airfoil (pick (0.5, 0))
control_points = [(0.5, 0.0)]

# (Optional) Material
mat = sp_pre.Material(
    name="Aluminum",
    elastic_modulus=70e3,
    poissons_ratio=0.33,
    yield_strength=250,
    density=2700,
    color="lightgrey"
)

# Create the geometry object
airfoil_geom = Geometry.from_points(
    points=airfoil_pts,
    facets=facets,
    control_points=control_points,
    material=mat
)



from sectionproperties.analysis.section import Section

# Mesh airfoil
airfoil_geom.create_mesh(mesh_sizes=[0.001])  # smaller = finer mesh

# Create section object
sec = Section(geometry=airfoil_geom)

# Run calculations
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
sec.calculate_plastic_properties()

print("Area:", sec.get_area())
print("Centroid (cx, cy):", sec.get_c())
# print("Moments of inertia about centroid (ixx, iyy, ixy):", sec.get_ic())
# print("Torsion constant J:", sec.get_j())
# print("Shear centre Gamma:", sec.get_gamma())
# print("Plastic modulus (Zx, Zy):", sec.get_z())

# Plot mesh and centroid
sec.plot_mesh()
sec.plot_centroids()
