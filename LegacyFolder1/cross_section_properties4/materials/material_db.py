# cross_section_properties/materials/material_db.py

from sectionproperties.pre import Material

def aluminum():
    return Material(
        name="Aluminum",
        elastic_modulus=70e3,
        poissons_ratio=0.33,
        yield_strength=250,
        density=2700,
        color="lightgrey"
    )

def steel():
    return Material(
        name="Steel",
        elastic_modulus=210e3,
        poissons_ratio=0.3,
        yield_strength=250,
        density=7850,
        color="grey"
    )

def carbon_epoxy():
    return Material(
        name="CFRP (uni)",
        elastic_modulus=140e3,
        poissons_ratio=0.25,
        yield_strength=1200,
        density=1600,
        color="black"
    )
