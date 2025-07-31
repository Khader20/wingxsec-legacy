import numpy as np
from scipy.interpolate import interp1d

def naca_4_series(digits: str, chord: float = 1.0, n_points: int = 200) -> np.ndarray:
    """
    Generate coordinates for a NACA 4-digit airfoil (e.g., '2412').
    Returns array shape (n_points*2-1, 2) for upper + lower, ordered clockwise.
    """
    m = int(digits[0]) / 100
    p = int(digits[1]) / 10
    t = int(digits[2:]) / 100

    x = np.linspace(0, 1, n_points)
    yt = 5 * t * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )
    yc = np.where(
        x < p,
        m / p**2 * (2 * p * x - x**2),
        m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2)
    ) if m != 0 and p != 0 else np.zeros_like(x)
    dyc_dx = np.where(
        x < p,
        2 * m / p**2 * (p - x),
        2 * m / (1 - p)**2 * (p - x)
    ) if m != 0 and p != 0 else np.zeros_like(x)
    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    # Order upper surface (from TE to LE) then lower (LE to TE)
    x_full = np.concatenate([xu[::-1], xl[1:]])
    y_full = np.concatenate([yu[::-1], yl[1:]])
    coords = np.column_stack([x_full * chord, y_full * chord])
    return coords

def load_from_dat(filepath: str, chord: float = 1.0, n_points: int = 200) -> np.ndarray:
    """
    Load airfoil coordinates from a .dat file and interpolate to (n_points*2-1,2).
    Supports XFOIL/UIUC format, rescaling by chord.
    """
    raw = np.loadtxt(filepath, comments=["#", "!", ">", ";"])
    if raw.shape[1] > 2:
        raw = raw[:, :2]
    x, y = raw[:, 0], raw[:, 1]
    # Remove duplicate (1,0), (0,0), etc.
    xy = np.unique(np.column_stack((x, y)), axis=0)
    # Split upper/lower surfaces by monotonic x or sign(y)
    le_idx = np.argmin(xy[:, 0])
    upper = xy[:le_idx+1]
    lower = xy[le_idx:][::-1]
    # Interpolate to uniform spacing
    for surf in [upper, lower]:
        if len(surf) < 2:
            raise RuntimeError("Surface too short after parsing .dat!")
    def interp_surface(surf, n):
        s = np.insert(np.cumsum(np.linalg.norm(np.diff(surf, axis=0), axis=1)), 0, 0)
        s_norm = s / s[-1]
        x_new = np.linspace(0, 1, n)
        f_x = interp1d(s_norm, surf[:, 0])
        f_y = interp1d(s_norm, surf[:, 1])
        return np.column_stack((f_x(x_new), f_y(x_new)))
    upper_i = interp_surface(upper, n_points)
    lower_i = interp_surface(lower, n_points)
    # Reorder: TE→LE (upper), LE→TE (lower)
    coords = np.vstack([upper_i[::-1], lower_i[1:]]) * chord
    return coords

def airfoil_with_thickness(coords: np.ndarray, thickness: float = 0.0):
    """
    Returns: - If thickness==0, just returns outer as filled airfoil
             - If thickness>0, returns outer, inner curves for shell (hollow)
    """
    from shapely.geometry import Polygon
    outer_poly = Polygon(coords)
    if thickness <= 0:
        return outer_poly, None
    inner_poly = outer_poly.buffer(-thickness, join_style=2)
    if inner_poly.is_empty or not inner_poly.is_valid:
        raise ValueError(f"Thickness {thickness} too large for airfoil geometry.")
    # If multipolygon, keep largest
    if inner_poly.geom_type == "MultiPolygon":
        inner_poly = max(inner_poly.geoms, key=lambda p: p.area)
    return outer_poly, inner_poly
