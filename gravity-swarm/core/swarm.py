import numpy


def dist(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5


def calc_dirc(x1, y1, x2, y2):
    return numpy.arctan2(x2-x1, y2-y1)


def update_speed(x, y, vx, vy, influences, swarm_data):
    for inf in influences:
        r = dist(x, y, inf["x"], inf["y"])
        if inf["kind"] == "grav":
            inf_dirc = calc_dirc(x, y, inf["x"], inf["y"])
            dx = inf["wx"] * numpy.sin(inf_dirc) * 1/(r**2)
            dy = inf["wy"] * numpy.cos(inf_dirc) * 1/(r**2)
        elif inf["kind"] == "vec":
            dx = inf["wx"] * 1/(r**2)
            dy = inf["wy"] * 1/(r**2)
        elif inf["kind"] == "wind":
            dx = inf["wx"] - inf["resistance"]*vx
            dy = inf["wy"] - inf["resistance"]*vy
        vx += dx
        vy += dy
    return (vx, vy)


def update_position(x, y, vx, vy, swarm_data):
    new_x = x + swarm_data["step_len"] * vx
    new_y = y + swarm_data["step_len"] * vy
    return (new_x, new_y)


def draw_point(x, y, i, swarm_data, canvas):
    X, Y = int(x), int(y)
    width = len(canvas)
    height = len(canvas[0])
    if 0 <= X < width and 0 <= Y < height:
        j = i / swarm_data["steps"]
        canvas[Y, X, 0] = min(canvas[Y, X, 0] + j * 60, 255)
        canvas[Y, X, 1] = min(canvas[Y, X, 1] + j * 80, 255)
        canvas[Y, X, 2] = min(canvas[Y, X, 2] + j * 120, 255)


def simulate_zergling(x, y, vx, vy, canvas, influences, swarm_data):
    for i in range(swarm_data["steps"]):
        draw_point(x, y, i, swarm_data, canvas)
        x, y = update_position(x, y, vx, vy, swarm_data)
        vx, vy = update_speed(x, y, vx, vy, influences, swarm_data)
