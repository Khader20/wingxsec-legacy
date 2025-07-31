# cross_section_properties/helpers.py

import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint

def ensure_closed(coords):
    """Ensure polygon is closed and all (x, y) are float."""
    coords = np.asarray(coords)
    if coords.shape[0] == 0:
        return []
    if not np.allclose(coords[0], coords[-1]):
        coords = np.vstack([coords, coords[0]])
    return [ (float(pt[0]), float(pt[1])) for pt in coords ]

def get_interior_point(coords):
    """
    Return a point guaranteed inside a (possibly nonconvex) polygon (uses Shapely).
    Starts with centroid; samples grid if centroid is not inside.
    """
    coords = ensure_closed(coords)
    poly = ShapelyPolygon(coords)
    centroid = poly.centroid
    if poly.contains(centroid):
        return (float(centroid.x), float(centroid.y))
    xs, ys = zip(*coords)
    for frac in np.linspace(0.1, 0.9, 9):
        pt = (min(xs) + frac*(max(xs)-min(xs)), min(ys) + frac*(max(ys)-min(ys)))
        if poly.contains(ShapelyPoint(pt)):
            return pt
    return (float(centroid.x), float(centroid.y))
