import random
import time
from random import randint
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageChops, ImageStat

# Type definitions
tyPosition = Tuple[int, int]

tyColor = Tuple[int, int, int, int]
tyShape = dict
tyElement = Tuple[str, tyShape, tyColor]
tyImage = Tuple[tyColor, List[tyElement]]

tyQuality = float
tyPop = List[Tuple[tyQuality, tyImage]]

# Constants
VALID_SHAPES = ["circle", "rectangle", "line"]
WIGGLE_MOVE_F = 0.1
WIGGLE_SHAPE_F = 0.2


# =============================================================================
# Generate Random Shape


def random_color(has_alpha)->tyColor:
    alpha = randint(0, 256) if has_alpha else 256
    return (randint(0, 256), randint(0, 256), randint(0, 256), alpha)


def random_shape(width: int, height: int, kind: str, **specs)-> tyShape:
    if kind == "circle":
        point = randint(0, width), randint(0, height)
        r = specs.get("approx_r", randint(5, 100)) * (2 * random.random())
        return {"p": point, "r": r}

    elif kind == "rectangle":
        point = randint(0, width), randint(0, height)
        width = specs.get("approx_w", randint(5, 100)) * (2 * random.random())
        height = specs.get("approx_h", randint(5, 100)) * (2 * random.random())
        return {"p": point, "w": width, "h": height}

    elif kind == "line":
        point1 = randint(0, width), randint(0, height)
        point2 = randint(0, width), randint(0, height)
        width = specs.get("approx_line_w", randint(1, 5))
        return {"p1": point1, "p2": point2, "w": width}

    else:
        raise Exception(f"Unknown shape kind `{kind}`")


def random_element(width: int, height: int, specs={})-> tyElement:
    kind = random.choice(specs.get("kinds", VALID_SHAPES))
    shape = random_shape(width, height, kind, **specs)
    color = random_color(specs.get("has_alpha", False))
    return (kind, shape, color)


def random_image(width: int, height: int, n_els: int, specs={})-> tyImage:
    background = random_color(has_alpha=False)
    elements = [random_element(width, height, specs) for _ in range(n_els)]
    return (background, elements)

# =============================================================================
# Specialisations


def wiggle_point(move, x, y):
    xx = round(random.gauss(x, move))
    yy = round(random.gauss(y, move))
    return (xx, yy)


def wiggle(width, height, element: tyElement, intensity: float)-> tyElement:
    """Returns a new element with a slightly altered shape."""
    kind, shape, color = element
    size = max(width, height)
    move = (size * WIGGLE_MOVE_F) * intensity
    f = WIGGLE_SHAPE_F

    if kind == "circle":
        p = wiggle_point(move, *shape["p"])
        r = abs(random.gauss(shape["r"], shape["r"]*f*intensity))
        new_shape = {"p": p, "r": r}

    elif kind == "rectangle":
        p = wiggle_point(move, *shape["p"])
        w = abs(random.gauss(shape["w"], shape["w"]*f*intensity))
        h = abs(random.gauss(shape["h"], shape["h"]*f*intensity))
        new_shape = {"p": p, "w": w, "h": h}

    elif kind == "line":
        p1 = wiggle_point(move, *shape["p1"])
        p2 = wiggle_point(move, *shape["p2"])
        w = abs(round(random.gauss(shape["w"], shape["w"]*f*intensity)))
        new_shape = {"p1": p1, "p2": p2, "w": w}

    else:
        raise Exception(f"Unknown shape kind `{kind}`")

    return (kind, new_shape, color)


def adjust_colors(r, g, b, a, d, has_alpha=False):

    m_r = max(0, min(255, round(random.gauss(r, d))))
    m_g = max(0, min(255, round(random.gauss(g, d))))
    m_b = max(0, min(255, round(random.gauss(b, d))))
    m_a = max(0, min(255, round(random.gauss(a, d)))) if has_alpha else a

    return (m_r, m_g, m_b, m_a)


def recolor(element: tyElement, intensity: float, has_alpha=False)-> tyElement:
    kind, shape, color = element
    d = (256 * intensity)**0.5

    return kind, shape, adjust_colors(*color, d, has_alpha)


# =============================================================================
# Draw Image

def draw_element(draw: ImageDraw, element: tyElement):
    """ Draws the element onto the image. """
    kind, shape, color = element

    if kind == "circle":
        x, y = shape["p"]
        r = shape["r"]
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    elif kind == "rectangle":
        x, y = shape["p"]
        dx, dy = shape["w"]/2, shape["h"]/2
        draw.rectangle([x-dx, y-dy, x+dx, y+dy], fill=color)

    if kind == "line":
        draw.line([shape["p1"], shape["p2"]], width=shape["w"], fill=color)
    return


def draw_image(width: int, height: int, image: tyImage)-> Image:
    background, elements = image
    canvas = Image.new("RGB", (width, height), background)
    draw_handle = ImageDraw.Draw(canvas, "RGBA")

    for element in elements:
        draw_element(draw_handle, element)

    return canvas


def evaluate_image(image: tyImage, real_image: Image)-> float:
    """Calculates the difference between the image and the drawing."""
    drawn_image = draw_image(real_image.width, real_image.height, image)

    diff_img = ImageChops.difference(drawn_image, real_image)

    stats = ImageStat.Stat(diff_img)

    return sum(stats.mean)/4

# =============================================================================
# TEMPORARY TESTING STUFF


def seed_population(n_els: int, n_images: int, real_image, rand_specs)-> tyPop:
    w, h = real_image.width, real_image.height

    images = [
        random_image(w, h, n_els, specs=rand_specs) for _ in range(n_images)]
    pop = [(evaluate_image(img, real_image), img) for img in images]

    return pop



def mutate_image(width: int, height: int, image: tyImage, specs={})-> tyImage:
    mutation = random.choice(["reshuffle", "replace"])
    bg, els = image
    new_els = els.copy()

    if mutation == "reshuffle":
        i, j = randint(0, len(els)-1), randint(0, len(els)-1)
        new_els[i], new_els[j] = new_els[j], new_els[i]
    
    elif mutation == "replace":
        i = randint(0, len(els)-1)
        new_els[i] = random_element(width, height, specs=specs)

    return bg, new_els



def evolve_image(n_els: int, in_path: str, out_path: str):

    rand_specs = {
        "kinds": ["rectangle", "circle", "line"],
        "approx_r": 30,
        "approx_h": 30,
        "approx_w": 30,
        "approx_line_w": 5,
    }

    real_image = Image.open(in_path)
    w, h = real_image.width, real_image.height

    improvement_steps = 1010
    exploration_step = 100
    pop_size = 64

    pop = seed_population(n_els, pop_size, real_image, rand_specs)
    
    t = time.time()
    for i in range(improvement_steps+1):
        intensity = (1.2 - (i / improvement_steps)) / 2
        
        improved_pop = []
        for fit, img in pop:
            bg, els = img

            for _ in range(10):
                new_bg = adjust_colors(*bg, (256 * intensity)**0.5)
                new_fit = evaluate_image((new_bg, els), real_image)
                if new_fit < fit:
                    fit = new_fit
                    bg = new_bg

            for j in range(len(els)):
                for _ in range(10):
                    recolored = els.copy()
                    recolored[j] = recolor(els[j], intensity)

                    new_fit = evaluate_image((bg, recolored), real_image)
                    if new_fit < fit:
                        fit = new_fit
                        els = recolored

            for j in range(len(els)):
                for _ in range(10):
                    wiggled = els.copy()
                    wiggled[j] = wiggle(w, h, els[j], intensity)

                    new_fit = evaluate_image((bg, wiggled), real_image)
                    if new_fit < fit:
                        fit = new_fit
                        els = wiggled

            improved_pop.append((fit, (bg, els)))

        pop = improved_pop

        if i % 10 == 0:
            now = time.time()
            dt, t = now-t, now
            print(
                f"{i}/{improvement_steps} ({round(i/improvement_steps*100)}%)  [best fit: {min(pop, key=lambda x: x[0])[0]:.4f}, worst fit: {max(pop, key=lambda x: x[0])[0]:.4f}, time: {dt:.3f}]")

        if i % 100 == 0:
            best = min(pop, key=lambda x: x[0])[1]
            canvas = draw_image(w, h, best)
            canvas.save("z"+str(i)+out_path)

        if i % exploration_step == 0:
            pop.sort(key=lambda x: x[0])
            good = pop[:len(pop)//2]
            opts = [
                mutate_image(w, h, image, specs=rand_specs) 
                for fit, image in good]
            evals = [evaluate_image(img, real_image) for img in opts]
            pop = good + list(zip(evals, opts))



    for fit, img in pop:
        canvas = draw_image(w, h, img)
        canvas.save("final_"+str(fit)+"_"+out_path)

    return
