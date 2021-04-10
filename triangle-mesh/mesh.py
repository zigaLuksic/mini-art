import random
from random import randint
from typing import List, Tuple
from PIL import Image, ImageDraw

# Type definitions
tyPosition = Tuple[float, float]

tyColor = Tuple[int, int, int, int]
tyColors = List[tyColor]

tyVertex = dict
tyVertices = List[List[tyVertex]]

tyMesh = Tuple[tyVertices, tyColors]

# =============================================================================


def random_color()->tyColor:
    return (randint(0, 255), randint(0, 255), randint(0, 255), 255)


def make_vertex(position: tyPosition, safety_r: float, mutable=True)-> tyVertex:
    vertex = {
        "original_p": position,
        "current_p": position,
        "safety_r": safety_r,
        "mutable": mutable}
    return vertex


def make_mesh(width: int, height: int, rows: int, points_per_row: int)-> tyMesh:
    n_triangles = 2 * (points_per_row - 1) * rows
    triangle_w = width / (points_per_row - 1.5)
    triangle_h = height / rows

    colors = [random_color() for _ in range(n_triangles)]

    # the maximum radius of disjoint circles with centers in vertices
    triangle_side = ((triangle_w / 2) ** 2 + triangle_h ** 2) ** 0.5
    R = min(triangle_side, triangle_w) / 2

    vertices = []
    for r in range(rows+1):
        row = []
        y = height * r / rows

        shift_start = r % 2 == 1  # marks if the row starts with a half triang
        is_mutable = r % rows != 0  # locks first and last row

        # add points in row (first and last separately)
        row.append(make_vertex((0, y), R, mutable=False))

        for i in range(1, points_per_row - 1):
            x = i * triangle_w - (triangle_w / 2 if shift_start else 0)
            row.append(make_vertex((x, y), R, mutable=is_mutable))

        row.append(make_vertex((width, y), R, mutable=False))

        vertices.append(row)

    return (vertices, colors)


def copy_mesh(mesh: tyMesh):
    vertices, colors = mesh
    colors_copy = [c for c in colors]

    vertices_copy = []
    for row in vertices:
        row_copy = [{k: v for k, v in vertex.items()} for vertex in row]
        vertices_copy.append(row_copy)

    return (vertices_copy, colors_copy)


def scale_mesh(mesh: tyMesh, factor: float):
    vertices, colors = mesh
    colors_copy = [c for c in colors]

    def scale_point(p):
        return (p[0] * factor, p[1] * factor)

    vertices_copy = []
    for row in vertices:
        row_copy = []
        for vertex in row:
            vertex_copy = {
                "original_p": scale_point(vertex["original_p"]),
                "current_p": scale_point(vertex["current_p"]),
                "safety_r": vertex["safety_r"] * factor,
                "mutable": vertex["mutable"]}
            row_copy.append(vertex_copy)

        vertices_copy.append(row_copy)

    return (vertices_copy, colors_copy)


def draw_mesh(draw: ImageDraw, mesh: tyMesh, bordercol=None, borderwidth=None):
    vertices, colors = mesh
    n_rows = len(vertices) - 1
    points_per_row = len(vertices[0])

    for r in range(n_rows):
        shift = 1 - r % 2

        # top half of triangles
        for i in range(points_per_row-1):
            points = [
                vertices[r][i]["current_p"],
                vertices[r][i+1]["current_p"],
                vertices[r+1][i+shift]["current_p"]]
            color = colors[r * 2 * (points_per_row - 1) + i]
            draw.polygon(points, fill=color)
            if bordercol is not None and borderwidth is not None:
                draw.line(points+[points[0]], width=borderwidth, fill=bordercol, joint="curve")

        # bot half of triangles
        for i in range(points_per_row-1):
            points = [
                vertices[r][i+(1-shift)]["current_p"],
                vertices[r+1][i]["current_p"],
                vertices[r+1][i+1]["current_p"]]
            color = colors[(r * 2 + 1) * (points_per_row - 1) + i]
            draw.polygon(points, fill=color)
            if bordercol is not None and borderwidth is not None:
                draw.line(points+[points[0]], width=borderwidth, fill=bordercol, joint="curve")

# =============================================================================
# Mutations


def wiggle_vertex(vertex: tyVertex, factor: float, safe_only)-> tyVertex:
    new_vertex = {k: v for k, v in vertex.items()}  # make copy

    if not vertex["mutable"]:
        return new_vertex

    move = vertex["safety_r"] * factor
    x, y = vertex["current_p"]
    orig_x, orig_y = vertex["original_p"]

    for _ in range(100):  # try a hundred times and then give up
        new_x = random.gauss(x, move)
        new_y = random.gauss(y, move)
        sq_dist = (orig_x - new_x)**2 + (orig_y - new_y)**2
        if sq_dist < vertex["safety_r"]**2 or not safe_only:
            new_vertex["current_p"] = (new_x, new_y)
            return new_vertex

    return new_vertex  # in case we fail to find a suitable point


def wiggle_color(color: tyColor, factor: float):
    (r, g, b, a) = color
    d = 50 * factor  # wild changes rarely pay off

    m_r = max(0, min(255, round(random.gauss(r, d))))
    m_g = max(0, min(255, round(random.gauss(g, d))))
    m_b = max(0, min(255, round(random.gauss(b, d))))

    return (m_r, m_g, m_b, a)


def combine_meshes(mesh1: tyMesh, mesh2: tyMesh, ratio=0.5)-> tyMesh:
    vertices1, colors1 = mesh1
    vertices2, colors2 = mesh2

    vertices, colors = [], []

    for i in range(len(colors1)):
        if random.random() < ratio:
            colors.append(colors1[i])
        else:
            colors.append(colors2[i])

    for r in range(len(vertices1)):
        row = []
        for i in range(len(vertices1[r])):
            if random.random() < ratio:
                row.append(vertices1[r][i].copy())
            else:
                row.append(vertices2[r][i].copy())
        vertices.append(row)

    return (vertices, colors)
