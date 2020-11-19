from core.universe import universe

print("========= Setting Universe =========")

test_universe = universe()
test_universe.set_canvas(width=1024, height=1024)

print("Ok!")

print("========= Setting Influences =========")

test_universe.add_influence(
    {"kind": "vec", "x": 256, "y": 212, "wx": 5, "wy": 5})

test_universe.add_influence(
    {"kind": "vec", "x": 612, "y": 324, "wx": 5, "wy": -10})

test_universe.add_influence(
    {"kind": "grav", "x": 268, "y": 712, "wx": 15, "wy": 15})

print("Ok!")

print("========= Setting Swarm =========")

test_universe.set_swarm(steps=3000, step_len=2)

print("Ok!")

print("========= Drawing =========")

waves = 1

for i in range(waves):
    #test_universe.draw_wall_swarm(1024, 0.3, 200)
    test_universe.draw_point_swarm(512, 512, 0.15, 360)
    print("Swarming wave {}/{}.".format(i+1, waves))

print("Ok!")

test_universe.show_image()
test_universe.save_image()