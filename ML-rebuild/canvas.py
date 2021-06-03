from rebuilder import rebuilder
from PIL import Image
import numpy as np


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


class double_canvas(canvas):
    def __init__(self, separation):
        super().__init__()
        self.original1 = None
        self.original2 = None
        self.separation = separation
        return

    def set_originals(self, picture_path1, picture_path2):
        self.original = Image.open(picture_path1)  # for rebuilding size/mode
        self.original1 = Image.open(picture_path1)
        self.original2 = Image.open(picture_path2)
        return

    def sample_original_old(self, n):
        """ Samples [original] for points that are known to rebuilders. """
        self.samples = {"where": [], "what": []}

        for i, original in (self.original1, self.original2):
            width, height = original.size


            for _ in range(n // 2):
                xi = np.random.randint(0, width - 1)
                yi = np.random.randint(0, height - 1)
                self.samples["where"].append([xi, yi])
                self.samples["what"].append(original.getpixel((xi, yi)))

        return

    def sample_original(self, n):
        """ Samples [original] for points that are known to rebuilders. """
        self.samples = {"where": [], "what": []}

        width, height = self.original1.size
        for _ in range(n // 2):
            xi = np.clip(int(np.random.beta(2, self.separation) * width), 0, width - 1)
            yi = np.clip(int(np.random.beta(2, self.separation) * height), 0, height - 1)
            self.samples["where"].append([xi, yi])
            self.samples["what"].append(self.original1.getpixel((xi, yi)))
                
        width, height = self.original2.size
        for _ in range(n // 2):
            xi = np.clip(int((1 - np.random.beta(2, self.separation)) * width), 0, width - 1)
            yi = np.clip(int((1 - np.random.beta(2, self.separation)) * height), 0, height - 1)
            self.samples["where"].append([xi, yi])
            self.samples["what"].append(self.original2.getpixel((xi, yi)))

        return