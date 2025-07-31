import numpy as np

def naca4_points(code: str, chord: float = 1.0, n_points: int = 120, x=None) -> np.ndarray:
    """
    Returns closed (N,2) array of points, CCW, for a NACA 4-digit airfoil.
    Optional: supply custom x array for trimmed/partial airfoil.
    """
    assert len(code) == 4 and code.isdigit()
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0

    if x is None:
        # Cosine spacing (LE to TE)
        beta = np.linspace(0, np.pi, n_points)
        x = (1 - np.cos(beta)) / 2 * chord
    else:
        x = np.array(x)
        chord = np.max(x)

    yt = 5 * t * chord * (
        0.2969 * np.sqrt(x/chord) - 0.1260*(x/chord) - 0.3516*(x/chord)**2 +
        0.2843*(x/chord)**3 - 0.1015*(x/chord)**4
    )

    if m == 0 and p == 0:
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
    else:
        yc = np.where(
            x < p*chord,
            m * x/(p**2) * (2*p - x/chord),
            m * (chord - x)/((1-p)**2) * (1 + x/chord - 2*p)
        )
        dyc_dx = np.where(
            x < p*chord,
            2*m/(p**2)*(p - x/chord),
            2*m/((1-p)**2)*(p - x/chord)
        )
    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)
    # Stack (LE->TE upper, TE->LE lower)
    coords = np.vstack([np.column_stack([xu, yu]), np.column_stack([xl[::-1], yl[::-1]])[1:]])
    # Ensure closure
    if not np.allclose(coords[0], coords[-1]):
        coords = np.vstack([coords, coords[0]])
    return coords

def naca4_skin_safe(code: str, chord: float, thickness: float, n_points: int = 120) -> tuple:
    """
    Returns (outer_pts, inner_pts) as (N,2) arrays for a hollow NACA 4-digit airfoil,
    with inner profile trimmed at both LE and TE for mesh-safe shell section.
    """
    assert thickness > 0 and thickness < chord/3, "Thickness must be positive and less than chord/3."
    trim = 2.2 * thickness  # Safe gap at LE and TE
    outer = naca4_points(code, chord=chord, n_points=n_points)
    x_inner = np.linspace(trim, chord - trim, n_points)
    inner = naca4_points(code, chord=chord, n_points=n_points, x=x_inner)
    return outer, inner
