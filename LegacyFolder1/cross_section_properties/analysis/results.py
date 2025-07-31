# cross_section_properties/analysis/results.py

def document_section(geoms):
    """
    Prints a table of all subregions: area, centroid, material, etc.
    """
    from rich.console import Console
    from rich.table import Table

    table = Table(title="Section Region Summary")
    table.add_column("Region", justify="right")
    table.add_column("Material")
    table.add_column("Area", justify="right")
    table.add_column("Centroid", justify="center")

    for i, geom in enumerate(geoms):
        try:
            area = geom.calculate_area()
            centroid = geom.calculate_centroid()
        except Exception:
            area = "?"
            centroid = "?"
        mat_name = getattr(geom.material, "name", str(geom.material))
        table.add_row(str(i), mat_name, str(area), str(centroid))

    Console().print(table)
