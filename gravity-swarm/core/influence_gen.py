import random
import numpy


def random_coords(width, height):
    return (random.randint(0, width-1), random.randint(0, height-1))


def random_grav(width, height, kind, approx_pow):
    x, y = random_coords(width, height)

    if kind == "sym":
        px = random.normalvariate(approx_pow, 0.1*approx_pow)
        py = random.normalvariate(approx_pow, 0.1*approx_pow)
    elif kind == "asym":
        diry = 2 * random.randint(0, 1)
        px = random.normalvariate(approx_pow, 0.2*approx_pow)
        py = random.normalvariate(approx_pow, 0.2*approx_pow) * (1-diry)
    else:
        px = random.normalvariate(0, approx_pow)
        py = random.normalvariate(0, approx_pow)

    return {"kind": "grav", "x": x, "y": y, "wx": px, "wy": py}


def random_vec(width, height, approx_pow):
    x, y = random_coords(width, height)

    dirc = random.random() * 2 * numpy.pi
    r = random.normalvariate(approx_pow, 0.3*approx_pow)
    px = numpy.sin(dirc)*r
    py = numpy.cos(dirc)*r

    return {"kind": "vec", "x": x, "y": y, "wx": px, "wy": py}


def random_wind(approx_pow):
    x, y = 0, 0
    dirc = random.random() * 2 * numpy.pi
    r = random.normalvariate(approx_pow, 0.1*approx_pow)
    px = numpy.sin(dirc)*r
    py = numpy.cos(dirc)*r

    wind = {"kind": "wind", "x": x, "y": y,
            "wx": px, "wy": py, "resistance": 0.01}
    return wind
