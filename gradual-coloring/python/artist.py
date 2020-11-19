from numpy.random import randint
import numpy as np
import PIL


def create_canvas(max_x, max_y):
    return np.zeros(shape=(max_y, max_x, 3))


class artist:

    def __init__(self, max_steps, max_tries):
        self.max_steps = max_steps
        self.max_tries = max_tries
        return

    def paint(self, ideal_picture):

        max_x, max_y = ideal_picture.size

        raw_pic = np.array(ideal_picture)
        raw_canvas = create_canvas(max_x, max_y)

        generator = self.option_generator(max_x, max_y)
        evaluator = self.option_evaluator(raw_pic, raw_canvas)

        for step in range(self.max_steps):
            if step % 1000 == 0:
                print(step)
            options = [generator(step) for x in range(0, self.max_tries)]
            evaluations = [evaluator(option) for option in options]

            best_option = min(evaluations, key=lambda eval: eval["error"])
            if best_option["error"] <= 0:
                self.paint_option(best_option, raw_canvas)

        return PIL.Image.fromarray(np.uint8(raw_canvas))

    def paint_option(self, best, canvas):
        (x1, y1), (x2, y2) = best["option"]
        r, g, b = best["red"], best["green"], best["blue"]

        canvas[y1: y2 + 1, x1: x2 + 1, 0].fill(r)
        canvas[y1: y2 + 1, x1: x2 + 1, 1].fill(g)
        canvas[y1: y2 + 1, x1: x2 + 1, 2].fill(b)

        return

    def option_generator(self, max_x, max_y):
        def gen(step):
            return self.generate_option(step, max_x, max_y)
        return gen

    def generate_option(self, step, max_x, max_y):
        dx = 1 + randint(0, high=50)
        dy = 1 + randint(0, high=50)
        x1, y1 = randint(0, high=max_x-dx), randint(0, high=max_y-dy)
        return ((x1, y1), (x1 + dx, y1 + dy))

    def option_evaluator(self, raw_pic, raw_can):

        def evaluator(option):
            r, r_err = self.evaluate_option(raw_pic, raw_can, 0, option)
            g, g_err = self.evaluate_option(raw_pic, raw_can, 1, option)
            b, b_err = self.evaluate_option(raw_pic, raw_can, 2, option)

            err = r_err + g_err + b_err

            return {"option": option, "red": r, "green": g, "blue": b,
                    "error": err}

        return evaluator

    def evaluate_option(self, raw_pic, raw_canvas, color, option):
        (x1, y1), (x2, y2) = option
        rel_pic = raw_pic[y1: y2 + 1, x1: x2 + 1, color]
        rel_canvas = raw_canvas[y1: y2 + 1, x1: x2 + 1, color]
        # Get averages
        avg_color = np.mean(rel_pic)
        # Evaluate
        old_mistake = np.mean(np.absolute(np.subtract(rel_pic, rel_canvas)))
        new_mistake = np.mean(np.absolute(np.subtract(rel_pic, avg_color)))
        return (avg_color, new_mistake - old_mistake)
