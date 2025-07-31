# cross_section_properties/material.py

class Material:
    """
    Stores mechanical properties for a section region.
    """
    def __init__(self, name, E, G, density, nu, color="#BBBBBB", yield_strength=1e9):
        self.name = name
        self.E = E
        self.G = G
        self.density = density
        self.nu = nu
        self.color = color
        self.yield_strength = yield_strength

    def __repr__(self):
        return f"Material({self.name}, E={self.E}, G={self.G}, ρ={self.density}, ν={self.nu})"
