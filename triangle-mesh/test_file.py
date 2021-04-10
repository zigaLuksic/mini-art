import evolution

name = "banara"

image_path = "{}.jpg".format(name)
out_name = "{}_mesh".format(name)

evolution_kwargs = {
    "rows": 15, "ppr": 24,
    "color_iterations": 3, "iterations": 22, "wiggles": 10,
    "pop_size": 4, "evo_step": 5,
}
draw_kwargs = {
    "safe": True, "upscale": 20, "borderwidth": None, "bordercol": (0, 0, 0, 255),
}


evolution.evolve_image(image_path, out_name, evolution_kwargs, draw_kwargs)
