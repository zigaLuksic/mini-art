from rebuilder import rebuilder
from PIL import Image
import random


class canvas:

    def __init__(self):
        """ A [canvas] requires three instances of [rebuilder] in order to
        rebuild the full RGB spectrum.

        It has a [original], which is the original image, and also a
        [rebuilt] which is the image rebuilt by rebuilders. """

        self.rebuilders = {
            "red": rebuilder(),
            "green": rebuilder(),
            "blue": rebuilder()}

        self.original = None
        self.rebuilt = None

        self.samples = None

        self.colors = {"red": 0, "green": 1, "blue": 2}
        return

    def set_original(self, picture_path):
        """ Copies the picture into [original]. """

        self.original = Image.open(picture_path)
        return

    def sample_original(self, n):
        """ Samples [original] for points that are known to rebuilders. """

        width, height = self.original.size
        samples = {"where": [], "what": []}

        for _ in range(n):
            xi = random.randint(0, width - 1)
            yi = random.randint(0, height - 1)
            samples["where"].append([xi, yi])
            samples["what"].append(self.original.getpixel((xi, yi)))

        self.samples = samples
        return

    def set_rebuilder_type(self, color, type):
        self.rebuilders[color].set_type(type, {})

    def rebuild(self):
        """ Creates [rebuilt] from samples by using rebuilders. """
        mode, size = self.original.mode, self.original.size

        # Gather samples
        it, at = self.samples["what"], self.samples["where"]

        colors = self.colors
        rebuilt_colors = {}

        # Inform rebuilders
        for c in colors:
            rebuilder = self.rebuilders[c]
            color_samples = {"where": at, "what": [x[colors[c]] for x in it]}
            rebuilder.inform(color_samples, size)
            rebuilt_colors[c] = [int(x) for x in rebuilder.rebuild()]

        # Construct a full vision
        rebuilt_image = list(zip(*(rebuilt_colors[col] for col in colors)))
        self.rebuilt = Image.new(mode, size)
        self.rebuilt.putdata(rebuilt_image)
        return

    def show_rebuilt(self):
        self.rebuilt.show()
        return
