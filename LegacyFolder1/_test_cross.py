import numpy as np
from rich import print
from rich.console import Console
from rich.table import Table
from rich.pretty import pprint, Pretty

console = Console()
import os


def colorful_line(char="*", length=130, style="bold blue"):
    console.print(char * length, style=style)
    return


from cross_section_properties.airfoil.generators import *
from cross_section_properties.geometry.airfoil_struct import AirfoilWithSpars
from sectionproperties.analysis.section import Section
from cross_section_properties.materials.material_db import *
from cross_section_properties.geometry.section_library import *
from sectionproperties.pre.geometry import CompoundGeometry
from cross_section_properties.geometry.utilities import *


""" Load Materials from YAML """
# Load all materials
all_materials = load_materials_as_dict("materials.yaml")
print("The Materials present in materials.yaml are:")
for mat in all_materials:
    print(mat)

# Get specific material by name
Alum_7075T6 = all_materials["Aluminum 7075-T6"]
Steel_S355 = all_materials["Steel S355"]
P12 = all_materials["Polyamide 12"]

# """ Generate NACA or load airfoil """
# chord = 0.2
# pts = naca4_points('0015', chord=chord, n_points=100)
# pts = repair_airfoil_trailing_edge(pts)
# # or
# # pts = import_dat('airfoil.dat', chord=chord)


# """ Build the Airfoil with Spars (if needed) """

# """ Spars """
# spars = [
#     {"x_chord": chord*0.1233, "thickness": 0.003, "material": P12},
#     {"x_chord": chord*0.66, "thickness": 0.005, "material": P12},
# ]
# builder = AirfoilWithSpars(
#     outer_pts=pts,
#     skin_thickness=0.003,
#     skin_material=P12,
#     # spar_specs=spars,
#     spar_specs=[],
# )

# 2. Generate and repair airfoil points
chord = 0.2
# pts = naca4_points('0015', chord=chord, n_points=20)
# pts = import_dat('naca0015.dat', chord=chord)
# pts = open_trailing_edge(pts, chord=chord, eps=1e-3)
# pts = blunt_trailing_edge(pts, chord=chord, dx=0.002)  # try dx = 0.002 or 0.004 (experiment)
# pts = naca4_points_blunt_te('0015', chord=chord, n_points=20, te_gap=0.000001)

from cross_section_properties.airfoil.generators import (
    load_naca4,
    load_from_dat,
    airfoil_with_thickness,
)

# Example: NACA 0015, skin 2mm
coords = load_naca4("0015", chord=0.2, n_points=120)
# or for .dat: coords = load_from_dat('naca0015.dat', chord=0.2, n_points=120)
outer_poly, inner_poly = airfoil_with_thickness(coords, thickness=0.002)

# If thickness=0, just use outer_poly
# If thickness>0, make skin region: outer_poly minus inner_poly


# import matplotlib.pyplot as plt
# pts = np.array(pts)
# plt.plot(pts[:,0], pts[:,1], marker="o")
# plt.axis("equal")
# plt.title("Blunted-TE Airfoil Polygon")
# plt.show()


import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# After creating pts and opening TE
outer = Polygon(pts)
from cross_section_properties.geometry.utilities import offset_polygon

try:
    inner_pts = offset_polygon(pts, 0.0)
    inner = Polygon(inner_pts)
    plt.plot(*zip(*pts), label="outer")
    plt.plot(*zip(*inner_pts), label="inner")
    plt.legend()
    plt.axis("equal")
    plt.show()
except Exception as e:
    print("Offset failed:", e)


# 3. Try building the airfoil with spars (robust to errors)
try:
    spars = [
        {"x_chord": chord * 0.1233, "thickness": 0.003, "material": P12},
        {"x_chord": chord * 0.66, "thickness": 0.005, "material": P12},
    ]
    builder = AirfoilWithSpars(
        outer_pts=pts, skin_thickness=0.0, skin_material=P12, spar_specs=[]  # or spars
    )
    airfoil_geom = builder.build()
except Exception as e:
    print(f"[bold red]Error constructing airfoil geometry: {e}[/bold red]")
    print(
        "[yellow]Try reducing skin_thickness, using fewer points, or check the airfoil shape.[/yellow]"
    )
    # Optional: plot points here for debugging
    import matplotlib.pyplot as plt

    plt.plot(*zip(*pts), marker="o")
    plt.title("Airfoil Points (Check for sharp TE or overlaps)")
    plt.show()
    exit(1)


# 1. Build airfoil (as above)
airfoil_geom = builder.build()


"""  """
# 2. Build I-beam and place it at the desired location (translate if needed)

I_Beam_main = i_beam(
    height=0.012,
    flange_width=0.050,
    web_thickness=0.006,
    flange_thickness=0.003,
    material=Alum_7075T6,
    center=(chord / 3, 0.0),
)


""" Combine all geometries (airfoil + I-beam + others) """
structure = assemble_section(airfoil_geom)

""" Mesh and analyze as usual """
structure.create_mesh(mesh_sizes=[0.0005])
sec = Section(geometry=structure)
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
# sec.calculate_plastic_properties()

# print("\nCross-section Area [m] :", sec.get_area())
# print("Cross-section Mass [kg/m] :", sec.get_mass())
# print("Cross-section Axial Rigidity EA [] :", sec.get_ea())
# print("modulus-weighted cross-section first moments of area [] :", sec.get_eq())
# print("modulus-weighted cross-section global second moments of area [] :", sec.get_eig())
# print("Cross-section elastic centroid [] :", sec.get_c())
# print("modulus-weighted cross-section centroidal second moments of area [] :", sec.get_eic())
# print("modulus-weighted cross-section centroidal elastic section moduli [] :", sec.get_ez())
# print("yield moment for bending about the centroidal axis [] :", sec.get_my())
# print("Cross-section centroidal radii of gyration [] :", sec.get_rc())
# print("modulus-weighted cross-section principal second moments of area [] :", sec.get_eip())
# print("Cross-section principal bending angle [] :", sec.get_phi())
# print("modulus-weighted cross-section principal elastic section moduli [] :", sec.get_ezp())
# print("yield moment for bending about the principal axis [] :", sec.get_my_p())
# print("Cross-section principal radii of gyration [] :", sec.get_rp())
# print("Cross-section effective Poisson's ratio [] :", sec.get_nu_eff())
# print("Cross-section effective elastic modulus [] :", sec.get_e_eff())
# print("Cross-section effective shear modulus [] :", sec.get_g_eff())
# print(" [] :", sec.get_c())

e_ref = Alum_7075T6.elastic_modulus
print(f"e_ref = {e_ref} [Pa]")

print()
colorful_line(char="+", length=100, style="bold cyan")
colorful_line(char="+", length=50, style="bold yellow")
console.print(f"[bold yellow]--- Geometric Analysis ---[/bold yellow]")
colorful_line(char="+", length=50, style="bold yellow")
print()

print(
    f"[bold green]Cross-section Area \[m^2][/bold green]: {sec.get_area()} || {sec.get_area()*1e6:.2f} \[mm^2]"
)
print(f"[bold green]Cross-section Perimeter \[m][/bold green]: {sec.get_perimeter()}")
print(f"[bold green]Cross-section Mass \[kg/m][/bold green]: {sec.get_mass():.4f}")
colorful_line(char="-", length=50, style="bold purple")

print(
    f"[bold orange1]Cross-section Axial Rigidity EA \[N][/bold orange1]: {sec.get_ea():.2f}"
)
print(
    f"[bold orange1]Cross-section Axial Rigidity A \[m^2][/bold orange1]: {sec.get_ea(e_ref)} || {sec.get_ea(e_ref)*1e6:.2f} \[mm^2]"
)
print(
    f"[bold orange1]Cross-section Modulus-weighted First Moments of Area EQ \[m^3][/bold orange1]: {sec.get_eq()}"
)
print(
    f"[bold orange1]Cross-section Modulus-weighted Global Second Moments of Area EIG \[N.m^2][/bold orange1]: {sec.get_eig()}"
)
print(
    f"[bold orange1]Cross-section Modulus-weighted Global Second Moments of Area IG \[m^4][/bold orange1]: {sec.get_eig(e_ref)}"
)
colorful_line(char="-", length=50, style="bold purple")


print(
    f"[bold green]Cross-section Elastic Centroid (cx, cy) \[m][/bold green]: {sec.get_c()}"
)
print(
    f"[bold green]Cross-section Modulus-weighted Centroidal Second Moments of Area EIC \[N.m^2][/bold green]: {sec.get_eic()}"
)
print(
    f"[bold green]Cross-section Modulus-weighted Centroidal Second Moments of Area EIC \[m^4][/bold green]: {sec.get_eic(e_ref)}\n"
)

print(
    f"Cross-section Modulus-weighted Centroidal Elastic Section Moduli EZ [m³]: {sec.get_ez()}"
)
print(f"Yield Moment for Bending about Centroidal Axis MY [N·m]: {sec.get_my()}\n")

print(f"Cross-section Centroidal Radii of Gyration RC [m]: {sec.get_rc()}")
print(
    f"Cross-section Modulus-weighted Principal Second Moments of Area EIP [N.m^2]: {sec.get_eip()}"
)
print(
    f"Cross-section Modulus-weighted Principal Second Moments of Area EIP [m^4]: {sec.get_eip(e_ref)}\n"
)

print(f"Cross-section Principal Bending Angle ϕ [radian]: {sec.get_phi()}")
print(
    f"Cross-section Modulus-weighted Principal Elastic Section Moduli EZP [m³]: {sec.get_ezp()}"
)
print(f"Yield Moment for Bending about Principal Axis MY_P [N·m]: {sec.get_my_p()}\n")

print(f"Cross-section Principal Radii of Gyration RP \[m]: {sec.get_rp()}")
print(f"Cross-section Effective Poisson's Ratio ν_eff [-]: {sec.get_nu_eff()}")
print(f"Cross-section Effective Elastic Modulus E_eff [Pa]: {sec.get_e_eff()}")
print(f"Cross-section Effective Shear Modulus G_eff [Pa]: {sec.get_g_eff()}")
# console.print(f"[bold red]---- EI \[N.m^2] = {sec.get_e_eff() * }[/bold red] \n")


print("\n[bold yellow]--- Warping (Torsion & Shear) Properties ---[/bold yellow]")
print(f"Modulus-weighted St Venant Torsion Constant EJ \[N.m^2]: {sec.get_ej()}")
print(f"Modulus-weighted St Venant Torsion Constant EJ \[m^4]: {sec.get_ej(e_ref)}")
console.print(
    f"[bold red]---- GJ \[N.m^2] = {(sec.get_e_eff()/(2*(1+sec.get_nu_eff()))) * sec.get_ej(e_ref)} || {sec.get_g_eff()*sec.get_ej(e_ref)}[/bold red] \n"
)

print(f"Centroidal Shear Centre (Elasticity) SC [m]: {sec.get_sc()}")
print(f"Principal Shear Centre (Elasticity) SC_P [m]: {sec.get_sc_p()}")
print(f"Centroidal Shear Centre (Trefftz) SC_T [m]: {sec.get_sc_t()}\n")

print(f"Modulus-weighted Warping Constant EGAMMA [m⁶]: {sec.get_egamma()}")
print(f"Modulus-weighted Centroidal Axis Shear Area EAS [m²]: {sec.get_eas()}")
print(f"Modulus-weighted Principal Axis Shear Area EAS_P [m²]: {sec.get_eas_p()}")
print(f"Global Monosymmetry Constants BETA [-]: {sec.get_beta()}")
print(f"Principal Monosymmetry Constants BETA_P [-]: {sec.get_beta_p()}")


sec.plot_mesh()
sec.plot_centroids()

# sec.display_results(fmt=".1f")
