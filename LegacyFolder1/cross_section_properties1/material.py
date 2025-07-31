# cross_section_properties/material.py

from typing import Optional

class Material:
    """
    Material class to store mechanical properties for section analysis.
    """
    def __init__(self,
                 name: str,
                 E: float,
                 G: float,
                 density: float,
                 nu: float,
                 color: Optional[str] = "#1f77b4"):
        """
        Initialize a new material.

        :param name: Material name/label
        :param E: Young's modulus [Pa]
        :param G: Shear modulus [Pa]
        :param density: Density [kg/m^3]
        :param nu: Poisson's ratio [-]
        :param color: Plot color (hex or string), optional
        """
        self.name = name
        self.E = E
        self.G = G
        self.density = density
        self.nu = nu
        self.color = color

    def __repr__(self):
        return (f"Material(name={self.name}, E={self.E:.2e}, G={self.G:.2e}, "
                f"density={self.density:.1f}, nu={self.nu}, color={self.color})")
    

# # ===== Example Usage =====
# if __name__ == "__main__":
#     from rich import print
#     # Example materials
#     CFRP = Material("CFRP", E=70e9, G=5e9, density=1600, nu=0.3, color="#2ca02c")
#     AL = Material("Aluminum", E=70e9, G=26e9, density=2700, nu=0.33, color="#1f77b4")
#     print(CFRP)
#     print(AL)
