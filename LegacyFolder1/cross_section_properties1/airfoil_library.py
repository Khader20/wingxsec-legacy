# cross_section_properties/airfoil_library.py

import numpy as np
import os

class AirfoilLibrary:
    """
    Static methods for airfoil geometry generation and import.
    """

    @staticmethod
    def load_from_dat(filepath: str, chord: float = 1.0, n_points: int = 200):
        """
        Load airfoil coordinates from a .dat file. Interpolates to n_points per surface.
        Supports standard .dat format (XFOIL, UIUC, ...).
        :param filepath: Path to .dat file
        :param n_points: Number of points to resample per surface (default 200)
        :return: (N,2) array of [x, y] coordinates, ordered clockwise
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"❌ Airfoil file '{filepath}' not found.")

        # Read lines, skip non-numeric
        coords = []
        with open(filepath, "r") as f:
            for line in f:
                tokens = line.strip().split()
                if len(tokens) == 2:
                    try:
                        coords.append([float(t) for t in tokens])
                    except Exception:
                        continue
        coords = np.array(coords)
        if coords.shape[1] != 2 or coords.shape[0] < 10:
            raise ValueError("❌ Invalid airfoil .dat file (must contain X Y coordinates).")
        
        # Resample for uniform point distribution (optional, for smooth FE mesh)
        from scipy.interpolate import splprep, splev
        x, y = coords[:, 0], coords[:, 1]
        # Parametrize points by chordwise distance
        s = np.linspace(0, 1, len(x))
        tck, u = splprep([x, y], s=0, per=0)
        unew = np.linspace(0, 1, n_points)
        x_new, y_new = splev(unew, tck)
        airfoil_coords = np.column_stack([x_new, y_new]) * chord
        return airfoil_coords

    @staticmethod
    def naca_4_series(code: str, chord: float = 1.0, n_points: int = 100):
        """
        Generate coordinates for a NACA 4-digit airfoil (symmetric or cambered).
        :param code: String, e.g. '2412', '0015'
        :param n_points: Number of points per surface (default 100)
        :return: (2*n_points, 2) array of [x, y] (upper surface from TE to LE, then lower surface LE to TE)
        """
        code = code.strip()
        if len(code) != 4 or not code.isdigit():
            raise ValueError(f"❌ Invalid NACA 4-digit code '{code}'.")
        m = int(code[0]) / 100.0
        p = int(code[1]) / 10.0
        t = int(code[2:]) / 100.0

        x = np.linspace(0, 1, n_points)
        yt = (t / 0.2) * (
            0.2969 * np.sqrt(x) -
            0.1260 * x -
            0.3516 * x**2 +
            0.2843 * x**3 -
            0.1015 * x**4
        )
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
        if m > 0 and p > 0:
            for i, xi in enumerate(x):
                if xi < p:
                    yc[i] = (m / p**2) * (2 * p * xi - xi**2)
                    dyc_dx[i] = (2 * m / p**2) * (p - xi)
                else:
                    yc[i] = (m / (1 - p)**2) * ((1 - 2*p) + 2*p*xi - xi**2)
                    dyc_dx[i] = (2 * m / (1 - p)**2) * (p - xi)
        theta = np.arctan(dyc_dx)
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)

        # Combine upper (from TE to LE) and lower (LE to TE)
        x_full = np.concatenate([xu[::-1], xl[1:]])
        y_full = np.concatenate([yu[::-1], yl[1:]])
        coords = np.column_stack([x_full, y_full]) * chord
        return coords



# # ===== Example Usage =====
# if __name__ == "__main__":
#     from rich import print
#     # Generate NACA 0015 coordinates
#     coords = AirfoilLibrary.naca_4_series('0015', n_points=200)
#     import matplotlib.pyplot as plt
#     plt.figure(figsize=(10,6))
#     plt.plot(coords[:, 0], coords[:, 1], color='orange', label="NACA 0015")
#     plt.scatter(coords[:, 0], coords[:, 1], c='k', marker='.', s=10)
#     plt.axis('equal'); plt.grid(True); plt.legend(); plt.title(f"NACA 0015 Airfoil | total # points = {len(coords)+1}"); plt.show()

#     # Example loading .dat (if you have data/NACA0012.dat, etc.)

#     current_file_dir = os.path.dirname(os.path.abspath(__file__))
#     project_root_dir = os.path.abspath(os.path.join(current_file_dir, '.'))
#     data_file_path = os.path.join(project_root_dir, "data", "naca0015.dat")

#     coords2 = AirfoilLibrary.load_from_dat(data_file_path, n_points=200)
#     plt.figure(figsize=(10,6))
#     plt.plot(coords2[:, 0], coords2[:, 1], color='blue' ,label="naca0015.dat")
#     plt.scatter(coords2[:, 0], coords2[:, 1], c='k', marker='.', s=10)
#     plt.axis('equal'); plt.grid(True); plt.legend(); plt.title(f"naca0015.dat Airfoil | total # points = {len(coords2)+1}"); plt.show()

#     print("[bold green]Finished AirfoilLibrary examples.[/bold green]")
