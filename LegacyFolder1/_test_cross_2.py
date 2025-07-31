import numpy as np
import matplotlib.pyplot as plt

from cross_section_properties.airfoil.generators import naca4_skin_safe
from cross_section_properties.materials.material_db import load_materials_as_dict
from sectionproperties.pre.geometry import Geometry
from sectionproperties.analysis.section import Section

# 1. Generate watertight skin
outer, inner = naca4_skin_safe('0015', chord=0.2, thickness=0.003, n_points=20)

# 2. Visual sanity check
plt.plot(outer[:,0], outer[:,1], label='Outer')
plt.plot(inner[:,0], inner[:,1], label='Inner')
plt.axis("equal")
plt.legend()
plt.title("NACA 0015 Airfoil Skin (Trimmed Inner, Mesh-Safe)")
plt.show()

# 3. Material
materials = load_materials_as_dict('materials.yaml')
mat = materials["Aluminum 7075-T6"]

# 4. Build Geometry (outer CCW, inner CW as hole)
points = list(map(tuple, outer[:-1])) + list(map(tuple, inner[:-1][::-1]))
n_outer = len(outer)-1
n_inner = len(inner)-1
facets = [(i, i+1) for i in range(n_outer-1)] + [(n_outer-1, 0)]
facets += [(n_outer+i, n_outer+i+1) for i in range(n_inner-1)] + [(n_outer+n_inner-1, n_outer)]
control_point = (0.1, 0.0)  # Near midchord

geom = Geometry.from_points(points, facets, [control_point], material=mat)

# 5. Mesh and analyze
geom.create_mesh(mesh_sizes=[0.0005])
sec = Section(geometry=geom)
sec.calculate_geometric_properties()
sec.plot_mesh()
sec.plot_centroids()
print("Area:", sec.get_area())
print("Centroid:", sec.get_c())
