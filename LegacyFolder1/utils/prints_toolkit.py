import numpy as np
from rich import print
from rich.console import Console
from rich.table import Table
from rich.pretty import pprint, Pretty
console = Console()

def section_title(title, style="bold yellow", char="═"):
    width = 130
    console.print(f"\n{char * width}", style=style)
    console.print(f"{title:^{width}}", style=style)
    console.print(f"{char * width}", style=style)
    return 

def colorful_print_matrix(matrix, title="Matrix"):
    import numpy as np

    # Ensure matrix is a NumPy array for easy processing
    arr = np.array(matrix)
    n_rows, n_cols = arr.shape

    section_title(title=title)
    table = Table(title="", show_header=False, show_lines=False, box=None)

    for _ in range(n_cols):
        table.add_column(justify="center")

    for row in arr:
        colored_row = []
        for val in row:
            if np.isclose(val, 0):
                color = "grey50"
            elif val > 0:
                color = "green"
            else:
                color = "red"
            # Formatting for floats/ints
            cell_str = f"[{color}]{val:.3g}[/{color}]"
            colored_row.append(cell_str)
        table.add_row(*colored_row)

    console.print(table)
    return 


def colorful_line(char="*", length=130, style="bold blue"):
    console.print(char * length, style=style)
    return 


def print_key_value_table(d, title="Properties", key_style="cyan", value_style="green"):
    """
    Key-Value Pretty Printing (for dicts, configs, results)
    """
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("Key", style=key_style)
    table.add_column("Value", style=value_style)

    for k, v in d.items():
        table.add_row(str(k), str(v))
    console.print(table)
    return 





def rich_progress_bar(task_iter, description="Processing"):
    """
    Progress Bar for Loops
    # Usage:
    for i in rich_progress_bar(range(100), "Looping"): ...
    """
    from rich.progress import Progress
    with Progress() as progress:
        task = progress.add_task(description, total=len(task_iter))
        for item in task_iter:
            yield item
            progress.update(task, advance=1)
    return 




def print_error(msg):
    console.print(f"[bold red]ERROR:[/bold red] {msg}")
    return 

def print_warning(msg):
    console.print(f"[bold yellow]WARNING:[/bold yellow] {msg}")
    return 


def pretty(obj):
    """
    Pretty Print Any Object/Dict
    """
    pprint(obj)
    return 





def print_nodes(nodes, title="Nodes Dict"):
    table = Table(title=title, show_lines=True)
    table.add_column("Key", style="bold cyan")
    table.add_column("Node Fields", style="white")

    for key, node in nodes.items():
        # Get all Node fields except methods
        node_dict = {k: v for k, v in vars(node).items()}
        table.add_row(
            str(key),
            Pretty(node_dict)
        )

    console.print(table)












def is_empty(val):
    if val is None:
        return True
    if isinstance(val, (str, bytes)) and len(val) == 0:
        return True
    if isinstance(val, (list, tuple, dict)) and len(val) == 0:
        return True
    if isinstance(val, np.ndarray) and val.size == 0:
        return True
    return False

def is_all_zeros(val):
    if isinstance(val, np.ndarray):
        return val.size > 0 and np.all(val == 0)
    if isinstance(val, (list, tuple)):
        return len(val) > 0 and all(v == 0 for v in val)
    return False

def print_nodes_table(nodes, title="Nodes Table || model.nodes"):
    if not nodes:
        console.print("[bold red]No nodes to display.[/bold red]")
        return

    first_node = next(iter(nodes.values()))
    field_names = list(vars(first_node).keys())

    field_style = {
        "idx": "bold cyan",
        "coords": "green",
        "bc": "yellow",
        "loads": "bold magenta",
        "dofs": "cyan",
        "displacement": "blue",
        "reaction": "red",
        "connected_nodes": "bright_green",
        "label": "purple",
        "extra": "dim"
    }
    def get_field_style(field): return field_style.get(field, "white")

    section_title(title=title)
    table = Table(title='', show_lines=True)
    table.add_column("Key", style="bold white")
    for field in field_names:
        table.add_column(field, style=get_field_style(field))

    for key, node in nodes.items():
        vals = []
        for field in field_names:
            val = getattr(node, field)

            # coords formatting
            if field == "coords":
                if is_all_zeros(val):
                    a = "[0]*"+str(val.size)
                    val_str = f"[yellow]{a}[/yellow]"
                elif is_empty(val):
                    val_str = "[dim]/[/dim]"
                else:
                    if isinstance(val, np.ndarray) and val.size > 8:
                        val_str = f"[bold blue]{val[:4].tolist()}... (shape {val.shape})[/bold blue]"
                    else:
                        val_str = f"[bold green]{val}[/bold green]"

            # bc formatting
            elif field == "bc":
                if isinstance(val, (list, tuple)) and len(val) > 0:
                    if all(v is False for v in val):
                        a = f"[False]*{len(val)}"
                        val_str = f"[dim white]{a}[/dim white]"
                    elif all(v is True for v in val):
                        val_str = f"[yellow][True]*{len(val)}[/yellow]"
                    else:
                        val_str = str(val)
                else:
                    val_str = "[dim]/[/dim]"

            # dofs formatting
            elif field == "dofs":
                if is_empty(val):
                    val_str = "[bold red]MISSING[/bold red]"
                else:
                    if isinstance(val, (list, tuple)) and len(val) > 8:
                        val_str = str(val[:4])[:-1] + ", ...]"
                    else:
                        val_str = f"[magenta]{str(val)}[/magenta]"

            # displacement formatting
            elif field == "displacement":
                if is_all_zeros(val):
                    a = "[0]*"+str(val.size)
                    val_str = f"[bold blue]{a}[/bold blue]"
                elif is_empty(val):
                    val_str = "[dim]/[/dim]"
                else:
                    if isinstance(val, np.ndarray) and val.size > 8:
                        val_str = f"[bold blue]{val[:4].tolist()}... (shape {val.shape})[/bold blue]"
                    else:
                        val_str = f"[bold blue]{val}[/bold blue]"

            # - formatting
            elif field == "reaction" or field == "loads":
                if is_all_zeros(val):
                    a = "[0]*"+str(+val.size)
                    val_str = f"[dim white]{a}[/dim white]"
                elif is_empty(val):
                    val_str = "[dim]/[/dim]"
                else:
                    if isinstance(val, np.ndarray) and val.size > 8:
                        val_str = f"[bold blue]{val[:4].tolist()}... (shape {val.shape})[/bold blue]"
                    else:
                        val_str = f"[bold blue]{val}[/bold blue]"



            elif field == "label":
                if val=="Wing":
                    val_str = f"[purple]{val}[/purple]"
                else:
                    if isinstance(val, np.ndarray) and val.size > 8:
                        val_str = f"[bold blue]{val[:4].tolist()}... (shape {val.shape})[/bold blue]"
                    else:
                        val_str = f"[bold yellow]{val}[/bold yellow]"

            # other fields: always check is_all_zeros before is_empty!
            elif is_all_zeros(val):
                val_str = "[0]*"+str(val.size)
            elif is_empty(val):
                val_str = f"[dim white]/[/dim white]"
            else:
                if isinstance(val, (list, tuple)) and len(val) > 8:
                    val_str = str(val[:4])[:-1] + ", ...]"
                elif isinstance(val, np.ndarray):
                    arr = val
                    if arr.size > 8:
                        val_str = f"{arr[:4].tolist()}... (shape {arr.shape})"
                    else:
                        val_str = str(arr)
                else:
                    val_str = str(val)

            vals.append(val_str)
        table.add_row(str(key), *vals)

    console.print(table)











def is_empty(val):
    if val is None:
        return True
    if isinstance(val, (str, bytes)) and len(val) == 0:
        return True
    if isinstance(val, (list, tuple, dict)) and len(val) == 0:
        return True
    if isinstance(val, np.ndarray) and val.size == 0:
        return True
    return False

def is_all_zeros(val):
    if isinstance(val, np.ndarray):
        return val.size > 0 and np.all(val == 0)
    if isinstance(val, (list, tuple)):
        return len(val) > 0 and all(v == 0 for v in val)
    return False

def print_elements_table(elements, title="Elements Table || model.elements"):
    if not elements:
        console.print("[bold red]No elements to display.[/bold red]")
        return

    # Get all field names from first element (including dataclass fields and extra keys)
    first_elem = elements[0]
    field_names = list(vars(first_elem).keys())

    # Assign colors for fields (customize as you want)
    field_style = {
        "idx": "orange1",
        "node_ids": "bold cyan",
        "material": "white",
        "section": "white",
        "other_data": "white",
        "label": "purple",
        "extra": "dim"
    }
    def get_field_style(field): return field_style.get(field, "white")

    section_title(title=title)
    table = Table(title='', show_lines=True)
    for field in field_names:
        table.add_column(field, style=get_field_style(field))

    for elem in elements:
        vals = []
        for field in field_names:
            val = getattr(elem, field)
            # Formatting for common fields
            if is_all_zeros(val):
                val_str = "[dim cyan][zeros][/dim cyan]"
            elif is_empty(val):
                val_str = "[dim]/[/dim]"
            else:
                if isinstance(val, (list, tuple)) and len(val) > 8:
                    val_str = str(val[:4])[:-1] + ", ...]"
                elif isinstance(val, np.ndarray):
                    arr = val
                    if arr.size > 8:
                        val_str = f"{arr[:4].tolist()}... (shape {arr.shape})"
                    else:
                        val_str = str(arr)
                elif hasattr(val, "__dict__"):  # For objects like Material, Section, OtherData
                    keys = list(vars(val).keys())
                    preview = {k: getattr(val, k) for k in keys[:3]}
                    if len(keys) > 3:
                        val_str = str(preview)[:-1] + ", ...}"
                    else:
                        val_str = str(preview)
                else:
                    val_str = str(val)
            vals.append(val_str)
        table.add_row(*vals)

    console.print(table)







# def print_mode_shape_table(full_modes: np.ndarray, mode_index: int, precision: int = 4):
#     """
#     Prints a table for the selected mode shape components from full_modes.
#     full_modes: shape (n_nodes, 6, n_modes)
#     mode_index: int, which mode to print
#     precision: decimal places for display
#     """
#     n_nodes = full_modes.shape[0]
#     col_names = [
#         "Node", 
#         "modeshape_x", 
#         "modeshape_y", 
#         "modeshape_z", 
#         "modeshape_Rx", 
#         "modeshape_Ry", 
#         "modeshape_Rz"
#     ]

#     table = Table(title=f"Mode shape {mode_index}", show_lines=False)
#     for col in col_names:
#         table.add_column(col, justify="right", style="cyan" if col != "Node" else "bold yellow")

#     for i in range(n_nodes):
#         row = [str(i)]
#         for j in range(6):
#             val = full_modes[i, j, mode_index]
#             row.append(f"{val:.{precision}e}")
#         table.add_row(*row)

#     console.print(table)
