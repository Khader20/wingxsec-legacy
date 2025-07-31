import json
from sectionproperties.pre import Material
from typing import Dict, List

def load_materials_from_json(json_path: str) -> List[Material]:
    with open(json_path, 'r') as f:
        data = json.load(f)
    mats = []
    for mat in data["materials"]:
        mats.append(Material(
            name=mat.get("name", "UserMaterial"),
            elastic_modulus=mat["elastic_modulus"],
            poissons_ratio=mat["poissons_ratio"],
            yield_strength=mat.get("yield_strength", 0),
            density=mat.get("density", 0),
            color=mat.get("color", "grey")
        ))
    return mats


import json
from sectionproperties.pre import Material
from typing import Dict

def load_materials_as_dict(json_or_yaml_path: str) -> Dict[str, Material]:
    """
    Loads a materials file (YAML or JSON) and returns a dictionary
    mapping material names to Material objects: all_mat[name]
    """
    import os

    ext = os.path.splitext(json_or_yaml_path)[-1].lower()
    if ext in ['.yaml', '.yml']:
        import yaml
        with open(json_or_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    elif ext == '.json':
        with open(json_or_yaml_path, 'r') as f:
            data = json.load(f)
    else:
        raise ValueError("File extension must be .yaml, .yml, or .json")

    mats = {}
    for mat in data["materials"]:
        mat_obj = Material(
            name=mat.get("name", "UserMaterial"),
            elastic_modulus=mat["elastic_modulus"],
            poissons_ratio=mat["poissons_ratio"],
            yield_strength=mat.get("yield_strength", 0),
            density=mat.get("density", 0),
            color=mat.get("color", "grey")
        )
        mats[mat_obj.name] = mat_obj
    return mats







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
