from core.universe import universe
from core.influence_gen import random_grav, random_vec, random_wind

print("========= Setting Universe =========")

width, height = 1024, 1024

test_universe = universe()
test_universe.set_canvas(width=width, height=height)

print("Ok!")

print("========= Setting Influences =========")

for i in range(3):
    inf = random_grav(width, height, "rand", 10)
    test_universe.add_influence(inf)

for i in range(3):
    inf = random_vec(width, height, 5)
    test_universe.add_influence(inf)

#test_universe.add_influence(random_wind(0.001))

print("Ok!")

print("========= Setting Swarm =========")

test_universe.set_swarm(steps=5000, step_len=2)

print("Ok!")

print("========= Drawing =========")

waves = 1

for i in range(waves):
    print("Swarming wave {}/{}.".format(i+1, waves))
    test_universe.draw_point_swarm(512, 512, 0.3, 100)
    # test_universe.draw_random_swarm(500)

test_universe.draw_wall_swarm(height, 0.2, 300)

print("Ok!")

test_universe.show_image()
test_universe.save_image()
test_universe.save_config()
