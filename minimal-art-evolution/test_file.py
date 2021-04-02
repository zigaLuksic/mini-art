import genetics

name = "nara"

in_path = "{}.jpg".format(name)
out_path = "{}_minimal.png".format(name)


steps = 1010
exploration_step = 100
pop_size = 2

genetics.evolve_image(10, pop_size, steps, exploration_step, in_path, out_path)
