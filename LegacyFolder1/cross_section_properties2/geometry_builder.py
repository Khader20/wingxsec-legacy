class CrossSectionBuilder:
    """
    Assembles regions for CompoundGeometry.
    """
    def __init__(self, solid_regions, hole_regions):
        self.solid_regions = solid_regions
        self.hole_regions = hole_regions

    def build(self):
        points = []
        facets = []
        control_points = []
        holes = []
        materials = []
        idx_offset = 0

        # Solids
        for region in self.solid_regions:
            pts, fcts = region.get_points_and_facets()
            cp = region.get_control_point()
            points.extend(pts)
            facets.extend([(i+idx_offset, j+idx_offset) for (i, j) in fcts])
            control_points.append(cp)
            materials.append(region.material)
            idx_offset += len(pts)
        # Holes
        for region in self.hole_regions:
            pts, fcts = region.get_points_and_facets()
            hp = region.get_control_point()
            points.extend(pts)
            facets.extend([(i+idx_offset, j+idx_offset) for (i, j) in fcts])
            holes.append(hp)
            idx_offset += len(pts)
        return points, facets, control_points, holes, materials
