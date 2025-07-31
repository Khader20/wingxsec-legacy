from rich import print
import numpy as np
import os

from cross_section_properties3.airfoil import naca_4_series
from cross_section_properties3.section_builder import (
    airfoil_with_thickness,
    get_spar_polygon,
    make_sectionproperties_geometry,
)
from sectionproperties.analysis import Section
import numpy as np

# 1. Airfoil outline (hollow shell or filled)
coords = naca_4_series("0015", chord=1.0, n_points=200)
outer, inner = airfoil_with_thickness(
    coords, thickness=0.02
)  # Set thickness=0 for filled

# 2. Spars (one or more)
spar1 = get_spar_polygon(outer, x_c=0.3, thickness=0.025)
spar2 = get_spar_polygon(outer, x_c=0.7, thickness=0.02)
spars = [spar1, spar2]

# 3. Holes (example: round cutout at x=0.6, y=0.25, r=0.06)
# hole_coords = [(0.6 + 0.06 * np.cos(a), 0.25 + 0.06 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 50)]
# hole = Polygon(hole_coords)
# holes = [hole]

# 4. Compose geometry for sectionproperties
geom = make_sectionproperties_geometry(outer, spars, inner_shell=inner)

# 5. Run mesh and analysis
geom.create_mesh(mesh_sizes=0.01)
sec = Section(geometry=geom)
sec.calculate_geometric_properties()
sec.calculate_warping_properties()
sec.display_results()
sec.plot_mesh()
sec.plot_centroids()
