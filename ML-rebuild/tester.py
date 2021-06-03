from canvas import canvas, double_canvas

img = double_canvas(3)
img.set_originals("img2.jpg", "img4.jpg")
img.sample_original(200)

img.set_rebuilder_type("red", "rich")
img.set_rebuilder_type("green", "rich")
img.set_rebuilder_type("blue", "rich")

img.rebuild()
img.show_rebuilt()
img.rebuilt.save("ML-rebuild-example.png")
