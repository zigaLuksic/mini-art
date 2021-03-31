import genetics

name = "nara"

in_path = "{}.jpg".format(name)
out_path = "{}_minimal.png".format(name)

genetics.evolve_image(10, in_path, out_path)
