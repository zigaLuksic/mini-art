import numpy
import random
import core.swarm as swarm
from PIL import Image


class universe:

    def __init__(self):
        self.canvas = None
        self.width = 0
        self.height = 0
        self.swarm_data = None
        self.influences = []
        self.draw_log = []

    def set_canvas(self, **settings):
        self.width = settings["width"]
        self.height = settings["height"]
        self.canvas = numpy.zeros(shape=(self.width, self.height, 3))

    def set_swarm(self, **settings):
        self.swarm_data = settings
        return

    def add_influence(self, influence):
        self.influences.append(influence)

    def log_drawing(self, log):
        self.draw_log.append(log)

    # ---------- Drawing functions ----------

    def draw_random_swarm(self, n):
        for _ in range(n):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            v_x, v_y = (2*random.random() - 1, 2*random.random() - 1)
            swarm.simulate_zergling(
                x, y, v_x, v_y, self.canvas, self.influences, self.swarm_data)
        self.log_drawing({"kind": "random", "n": n})
        return

    def draw_point_swarm(self, x, y, speed, n):
        for i in range(n):
            dirc = 2*numpy.pi * (i/n)
            v_x, v_y = speed * numpy.sin(dirc), speed * numpy.cos(dirc)
            swarm.simulate_zergling(
                x, y, v_x, v_y, self.canvas, self.influences, self.swarm_data)
        self.log_drawing(
            {"kind": "point", "point": (x, y), "speed": speed, "n": n})
        return

    def draw_wall_swarm(self, height, speed, n):
        for i in range(n):
            x, y = 0, i * (height / n)
            v_x, v_y = speed, 0
            swarm.simulate_zergling(
                x, y, v_x, v_y, self.canvas, self.influences, self.swarm_data)
        self.log_drawing(
            {"kind": "wall", "height": height, "speed": speed, "n": n})
        return

    # ---------- Image and Config functions ----------

    def show_image(self):
        image = Image.fromarray(numpy.uint8(self.canvas))
        image.show()
        return

    def save_image(self, name="temp.png"):
        image = Image.fromarray(numpy.uint8(self.canvas))
        image.save("temp.png")

    def save_config(self, name="config.txt"):
        # Canvas data
        canvas_config = "Width = {}, Height = {}".format(
            self.width, self.height)
        with open("config.txt", mode="w") as f:
            print("Canvas Config", file=f)
            print(canvas_config, file=f)
            print("\nSwarm Config", file=f)
            print(self.swarm_data, file=f)
            print("\nInfluences", file=f)
            print(self.influences, file=f)
            print("\nDraw Log", file=f)
            print(self.draw_log, file=f)
