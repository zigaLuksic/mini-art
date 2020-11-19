from numpy.random import randint
import numpy
import PIL


def create_canvas(max_x, max_y):
    return numpy.zeros(shape=(max_y, max_x, 3))


class lineartist:

    def __init__(self, max_steps, max_tries):
        self.max_steps = max_steps
        self.max_tries = max_tries
        return

    def paint(self, ideal_picture):

        max_x, max_y = ideal_picture.size

        raw_pic = numpy.array(ideal_picture)
        raw_canvas = create_canvas(max_x, max_y)

        generator = self.option_generator(max_x, max_y)
        evaluator = self.option_evaluator(raw_pic, raw_canvas)

        for step in range(self.max_steps):
            self.step = step
            if step % 100 == 0:
                print(step)
            max_tries = min(self.max_tries, 1 + step // 50)
            options = [generator() for x in range(0, max_tries)]
            evaluations = [evaluator(option) for option in options]

            best_option = max(evaluations, key=lambda eval: eval["error"])
            self.paint_option(best_option, raw_canvas)

        return PIL.Image.fromarray(numpy.uint8(raw_canvas))

    def relevant_ys(self, x, option):
        offset = option["offset"]
        poly = option["poly"]
        _, max_y = option["max_coords"]
        relevant_y = 1
        for i in range(len(poly)):
            relevant_y += (((x - offset)**i) * poly[i])
        relevant_y = int(relevant_y)
        width = (1 + int(30 * (self.max_steps - self.step) /
                         self.max_steps)) * len(poly)
        belt = list(range(-width, width))
        return [relevant_y + b for b in belt if 0 <= relevant_y + b < max_y]

    def paint_option(self, best, canvas):
        x_start, x_end = best["option"]["xrange"]
        r, g, b = best["red"], best["green"], best["blue"]

        for x in range(x_start, x_end):
            for y in self.relevant_ys(x, best["option"]):
                canvas[y, x, 0] = r
                canvas[y, x, 1] = g
                canvas[y, x, 2] = b

        return

    def option_generator(self, max_x, max_y):
        def gen():
            return self.generate_option(max_x, max_y)
        return gen

    def generate_option(self, max_x, max_y):
        degree = randint(1, 4)
        initial = numpy.random.uniform(0, max_y)
        linear = numpy.random.uniform(-5, 5)
        offset = numpy.random.uniform(0, max_x)
        poly = [initial] + [linear] + \
            [numpy.random.uniform(-0.001, 0.001) for _ in range(degree - 1)]
        length = randint(0, max_x // (1 + 3*(self.step / self.max_steps)))
        start = randint(0, max_x - length)
        option = {"max_coords": (max_x, max_y), "poly": poly,
                  "offset": offset, "xrange": (start, start + length)}
        return option

    def option_evaluator(self, raw_picture, raw_canvas):

        def evaluator(option):
            red, red_error = self.evaluate_option(
                raw_picture, raw_canvas, 0, option)
            green, green_error = self.evaluate_option(
                raw_picture, raw_canvas, 1, option)
            blue, blue_error = self.evaluate_option(
                raw_picture, raw_canvas, 2, option)

            error = red_error + green_error + blue_error
            evaluation = {"option": option, "red": red,
                          "green": green, "blue": blue, "error": error}

            return evaluation

        return evaluator

    def evaluate_option(self, raw_pic, raw_canvas, color, option):
        x_start, x_end = option["xrange"]
        sum = 0
        num = 1
        for x in range(x_start, x_end):
            for y in self.relevant_ys(x, option):
                sum += raw_pic[y, x, color]
                num += 1

        avg_color = sum // num
        improvement = 0
        for x in range(x_start, x_end):
            for y in self.relevant_ys(x,  option):
                old_error = abs(raw_pic[y, x, color] - raw_canvas[y, x, color])
                new_error = abs(raw_pic[y, x, color] - avg_color)
                improvement += (old_error - new_error)

        improvement = improvement // num

        return (avg_color, improvement)
