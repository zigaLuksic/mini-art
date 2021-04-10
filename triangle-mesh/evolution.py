import random
import time
import mesh as meshtools
from random import randint
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageChops, ImageStat

# Type definitions
tyPosition = Tuple[float, float]

tyColor = Tuple[int, int, int, int]
tyColors = List[tyColor]

tyVertex = dict
tyVertices = List[List[tyVertex]]

tyMesh = Tuple[tyVertices, tyColors]

tyPop = List[Tuple[float, tyMesh]]


def draw_image(width: int, height: int, mesh: tyMesh, **borderkwargs)-> Image:

    canvas = Image.new("RGB", (width, height))
    draw_handle = ImageDraw.Draw(canvas, "RGBA")

    meshtools.draw_mesh(draw_handle, mesh, **borderkwargs)

    return canvas


def evaluate_mesh(mesh: tyMesh, real_image: Image)-> float:
    """Calculates the difference between the image and the drawing."""
    drawn_image = draw_image(real_image.width, real_image.height, mesh)

    diff_img = ImageChops.difference(drawn_image, real_image)

    stats = ImageStat.Stat(diff_img)

    return sum(stats.mean)/4


def wiggle_mesh(mesh: tyMesh, real_image: Image, wiggle_steps: int, wiggle_factor: float,
                color_only=False, safe_only=True)-> tyMesh:

    new_mesh = meshtools.copy_mesh(mesh)
    best_fit = evaluate_mesh(new_mesh, real_image)
    vertices, colors = new_mesh

    for i in range(len(colors)):
        for _ in range(wiggle_steps):
            old_color = colors[i]
            new_color = meshtools.wiggle_color(old_color, wiggle_factor)

            colors[i] = new_color
            new_fit = evaluate_mesh(new_mesh, real_image)

            if new_fit < best_fit:
                best_fit = new_fit
            else:
                colors[i] = old_color

    if color_only:
        return new_mesh

    for r in range(len(vertices)):
        for i in range(len(vertices[r])):
            if not vertices[r][i]["mutable"]:
                continue

            for _ in range(wiggle_steps):
                old_vertex = vertices[r][i]
                new_vertex = meshtools.wiggle_vertex(old_vertex, wiggle_factor, safe_only)

                vertices[r][i] = new_vertex
                new_fit = evaluate_mesh(new_mesh, real_image)

                if new_fit < best_fit:
                    best_fit = new_fit
                else:
                    vertices[r][i] = old_vertex

    return new_mesh


def make_population(n_meshes: int, real_image: Image, n_rows: int, points_per_row: int)-> tyPop:
    w, h = real_image.width, real_image.height
    meshes = [
        meshtools.make_mesh(w, h, n_rows, points_per_row)
        for _ in range(n_meshes)]
    return [(evaluate_mesh(m, real_image), m) for m in meshes]


def evolve_population(pop: tyPop, real_image: Image)-> tyPop:
    pop.sort(key=lambda x: x[0])
    apex_members = pop[:len(pop)//2]
    offspring = []
    for _, mesh in apex_members:
        _, partner = random.choice(apex_members)  # can select itself again
        child = meshtools.combine_meshes(mesh, partner)
        fit = evaluate_mesh(child, real_image)
        offspring.append((fit, child))
    return apex_members+offspring


def evolve_image(image_path: str, out_name: str, evolution_kwargs, draw_kwargs={}, report=True):

    real_image = Image.open(image_path)
    w, h = real_image.width, real_image.height

    # Extract arguments
    rows, ppr = evolution_kwargs["rows"], evolution_kwargs["ppr"]

    pop_size = evolution_kwargs.get("pop_size", 1)
    evo_step = evolution_kwargs.get("evo_step", None)

    iterations, wiggles = evolution_kwargs["iterations"], evolution_kwargs.get("wiggles", 10)
    color_iterations = evolution_kwargs.get("color_iterations", 0)

    safe, upscale = draw_kwargs.get("safe", True), draw_kwargs.get("upscale", 1)
    borderkwargs = {k: v for k, v in draw_kwargs.items() if k in ("borderwidth", "bordercol")}

    # Start evolution
    pop = make_population(pop_size, real_image, rows, ppr)

    sep = "="*50+"\n"
    if report:
        print(sep+"color optimisation\n"+sep)

    t = time.time()
    for i in range(color_iterations):
        new_pop = []
        for fit, mesh in pop:
            new = wiggle_mesh(mesh, real_image, wiggles, 0.4, color_only=True)
            new_fit = evaluate_mesh(new, real_image)
            better = min((fit, mesh), (new_fit, new), key=lambda x: x[0])
            new_pop.append(better)

        pop = new_pop

        if report:
            best_fit, best_mesh = min(pop, key=lambda x: x[0])
            best_mesh = meshtools.scale_mesh(best_mesh, upscale)
            draw_image(w * upscale, h * upscale, best_mesh, **borderkwargs).save(f"{i+1}_{out_name}.png")
            t_now = time.time()
            t, dt = t_now, t_now - t
            print(f"{i+1}/{color_iterations} complete | average fit: {best_fit:.4f} | iteration time: {dt}s")

    if report:
        print(sep+"shape optimisation\n"+sep)

    for j in range(iterations):
        if pop_size > 1 and evo_step is not None and j % evo_step == 0:
            pop = evolve_population(pop, real_image)

        new_pop = []
        f = 0.4 - (0.3 * j/iterations)
        for fit, mesh in pop:
            new = wiggle_mesh(mesh, real_image, wiggles, f, safe_only=safe)
            new_fit = evaluate_mesh(new, real_image)
            better = min((fit, mesh), (new_fit, new), key=lambda x: x[0])
            new_pop.append(better)

        pop = new_pop

        if report:
            best_fit, best_mesh = min(pop, key=lambda x: x[0])
            best_mesh = meshtools.scale_mesh(best_mesh, upscale)
            draw_image(w*upscale, h*upscale, best_mesh, **borderkwargs).save(f"{i+j+2}_{out_name}.png")
            t_now = time.time()
            t, dt = t_now, t_now - t
            print(f"{j+1}/{iterations} complete | average fit: {best_fit:.4f} | iteration time: {dt}s")

    for fit, mesh in pop:
        upscale_mesh = meshtools.scale_mesh(mesh, upscale)
        draw_image(upscale * w, upscale * h, upscale_mesh, **borderkwargs).save(f"final_{fit}_"+out_name+".png")

    return
