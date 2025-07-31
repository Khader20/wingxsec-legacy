# cross_section_properties/airfoil/generators.py

import numpy as np
from typing import List, Tuple

def naca4_points(code: str, chord: float = 1.0, n_points: int = 100) -> List[Tuple[float, float]]:
    """
    Generate coordinates for a NACA 4-digit airfoil (e.g., '0012', '2412').
    Returns a closed polygon (upper + lower surface, CCW).
    """
    assert len(code) == 4 and code.isdigit(), "Code must be a string of 4 digits."
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0

    x = np.linspace(0, chord, n_points)
    yt = 5 * t * chord * (
        0.2969 * np.sqrt(x / chord) -
        0.1260 * (x / chord) -
        0.3516 * (x / chord) ** 2 +
        0.2843 * (x / chord) ** 3 -
        0.1015 * (x / chord) ** 4
    )

    if m == 0 and p == 0:
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
    else:
        yc = np.where(
            x < p * chord,
            m * x / (p ** 2) * (2 * p - x / chord),
            m * (chord - x) / ((1 - p) ** 2) * (1 + x / chord - 2 * p)
        )
        dyc_dx = np.where(
            x < p * chord,
            2 * m / (p ** 2) * (p - x / chord),
            2 * m / ((1 - p) ** 2) * (p - x / chord)
        )
    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)
    # Combine upper (LE -> TE) and lower (TE -> LE) for closed polygon
    coords = np.vstack([
        np.stack([xu, yu], axis=1),
        np.stack([xl[::-1], yl[::-1]], axis=1)[1:]
    ])
    return [tuple(pt) for pt in coords]

def import_dat(file_path: str) -> List[Tuple[float, float]]:
    """
    Import airfoil coordinates from a .dat file (e.g., UIUC/XFOIL format).
    Returns a closed polygon as a list of (x, y) tuples.
    """
    coords = []
    with open(file_path, "r") as f:
        lines = f.readlines()
    # Skip the first line if it's a header (not numeric)
    for line in lines:
        try:
            x, y = [float(val) for val in line.strip().split()]
            coords.append((x, y))
        except ValueError:
            continue  # skip headers or blank lines
    # Ensure closed (last = first)
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords
