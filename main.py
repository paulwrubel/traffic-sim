import sys, pygame, math
from pygame import time, display, draw, font
from pygame.math import Vector2
from config import *
from objects import *
from constants import *

def start():

    print("initializing pygame...")
    print(pygame.version.ver)
    pygame.init()

    print("initializing config...")
    screen_size = (1200, 750)
    framerate = 144
    config = Config(screen_size, framerate, pygame.SCALED)
    config.clock = time.Clock()
    config.screen = display.set_mode(config.size, config.flags)
    config.font = font.SysFont("arial", 20)

    print("initializing road...")
    # Car Units
    config.env["road_length"] = 40
    config.env["road_width"] = 0.85

    outer_road_diameter_pixels = config.height * 0.95
    road_diameter = config.env["road_length"] / math.pi
    outer_road_diameter = road_diameter + config.env["road_width"]

    config.env["cars_to_pixels"] = outer_road_diameter_pixels / outer_road_diameter
    config.env["pixels_to_cars"] = 1.0 / config.env["cars_to_pixels"]

    config.env["speed_limit"] = 3.5
    config.env["drag"] = -0.01
    config.env["light_brakes_acceleration"] = -0.20
    config.env["heavy_brakes_acceleration"] = -0.150

    config.env["max_acceleration"] = 0.5
    config.env["idle_acceleration"] = 0.03
    config.env["idle_speed"] = 0.03
    config.env["max_braking_acceleration"] = -1.0

    print("initializing cars...")
    config.env["cars"] = []
    car_count = 10

    car_default_speed = 0.0
    car_speeds = {}

    car_default_acceleration = 0.15
    car_accelerations = {
        1: 0.22, 
        2: 0.14, 
        3: 0.14, 
        4: 0.19, 
        5: 0.11, 
        6: 0.09,
        12: 0.01,
        15: 0.3,
    }

    car_default_variance = 0.0
    car_variances = {
        1: 0.5, 
        2: -0.20,
        3: 0.9,
        5: -0.4,
    }
    for i in range(1, car_count + 1):
        location = (i - 1) * (config.env["road_length"] / car_count)
        speed = car_default_speed if i not in car_speeds else car_speeds[i]
        acceleration = car_default_acceleration if i not in car_accelerations else car_accelerations[i]
        variance = car_default_variance if i not in car_variances else car_variances[i]
        config.env["cars"].append(Car(i, config, location, speed, acceleration, variance))

    while True:
        loop(config)

def loop(config):
    dt_millis = config.clock.tick(config.framerate)
    dt = dt_millis / 1000.0

    check_events(config)
    config.screen.fill(WHITE)

    road_outer_radius_pixels = int(((config.env["road_length"] / math.pi) + config.env["road_width"]) * 0.5 * config.env["cars_to_pixels"])
    road_inner_radius_pixels = int(((config.env["road_length"] / math.pi) - config.env["road_width"]) * 0.5 * config.env["cars_to_pixels"])

    draw.circle(config.screen, BLACK, config.center, road_outer_radius_pixels, 2)
    draw.circle(config.screen, BLACK, config.center, road_inner_radius_pixels, 2)
    draw.circle(config.screen, BLACK, config.center, 20, 5)

    for car in config.env["cars"]:
        car.update(config, dt)
        car.draw(config)
        text_surface = config.font.render(
            "Car " + str(car.label) + 
            " speed: " + format(car.speed, ".2f") + 
            ", accel: " + format(car.acceleration, ".2f"), 
                True, BLACK)
        config.screen.blit(text_surface, (0, car.label*25))

    text_surface = config.font.render("Current FPS: " + str(int(config.clock.get_fps())), True, BLACK)
    config.screen.blit(text_surface, (0, 0))
    display.flip()


def check_events(config):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            temp = config.screen
            config.screen = display.set_mode(event.size, config.flags)
            config.screen.blit(temp, (0, 0))
            del temp


if __name__ == "__main__":
    start()