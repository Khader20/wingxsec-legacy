from rich import print
import numpy as np
import os

from sectionproperties.pre import CompoundGeometry
from sectionproperties.analysis import Section
from cross_section_properties2.regions import AirfoilRegion, RobustSparRegion, CutoutRegion
from cross_section_properties2.geometry_builder import CrossSectionBuilder
from cross_section_properties2.airfoil import naca_4_series
from cross_section_properties2.material import Material
from cross_section_properties2.helpers import *


mat_skin = Material("CFRP", 70e9, 5e9, 1600, 0.3, "#2ca02c")
mat_spar = Material("Steel", 210e9, 81e9, 7850, 0.3, "#003366")

airfoil_coords = naca_4_series("2412", chord=100, n_points=180)
airfoil = AirfoilRegion(airfoil_coords, skin_thickness=2, material=mat_skin)

spar = RobustSparRegion(airfoil_coords, x_c=40, thickness=4, material=mat_spar, height_fraction=1.0)

hole_coords = [(70+5*np.cos(a), 25+5*np.sin(a)) for a in np.linspace(0, 2*np.pi, 50)]
hole = CutoutRegion(hole_coords)

solids = [airfoil, spar]
holes = []
if airfoil.hole_coords is not None:
    # AirfoilRegion has an internal shell (true void)
    holes.append(type("Region",(object,),{"coords":airfoil.hole_coords,
                                          "get_points_and_facets":lambda self: (ensure_closed(self.coords),
                                                                                [(i, i+1) for i in range(len(self.coords)-1)]),
                                          "get_control_point":lambda self: get_interior_point(self.coords)})())

holes.append(hole)

builder = CrossSectionBuilder(solids, holes)
points, facets, control_points, holes_cp, materials = builder.build()

geom = CompoundGeometry.from_points(
    points, facets, control_points, holes=holes_cp, materials=materials
)
geom.create_mesh(mesh_sizes=1.5)
sec = Section(geometry=geom)
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
sec.display_results()
sec.plot_mesh()
sec.plot_centroids()
