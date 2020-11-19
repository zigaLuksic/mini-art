from canvas import canvas

img = canvas()
img.set_original("ML-rebuild-starting.png")
img.sample_original(10000)

img.set_rebuilder_type("red", "rich")
img.set_rebuilder_type("green", "rich")
img.set_rebuilder_type("blue", "rich")

img.rebuild()
img.show_rebuilt()
img.rebuilt.save("ML-rebuild-example.png")
