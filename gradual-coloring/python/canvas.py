from PIL import Image
from artist import artist
from lineartist import lineartist
import random


class canvas:

    def __init__(self, steps, tries):
        self.ideal_picture = None
        self.drawn_picture = None
        self.artist = artist(steps, tries)
        return

    def set_ideal_picture(self, picture_path):
        self.ideal_picture = Image.open(picture_path)
        return

    def paint(self):
        self.drawn_picture = self.artist.paint(self.ideal_picture)
        return

    def show(self):
        self.drawn_picture.show()
        return
