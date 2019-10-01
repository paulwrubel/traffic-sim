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
    screen_size = (1200, 600)
    framerate = 144
    config = Config(screen_size, framerate, pygame.SCALED)
    config.clock = time.Clock()
    config.screen = display.set_mode(config.size, config.flags)
    config.font = font.SysFont("arial", 20)

    print("initializing road...")
    # Car Units
    config.env["road_length"] = 15.0
    config.env["road_width"] = 0.85

    outer_road_diameter_pixels = config.height * 0.8
    road_diameter = config.env["road_length"] / math.pi
    outer_road_diameter = road_diameter + config.env["road_width"]

    config.env["cars_to_pixels"] = outer_road_diameter_pixels / outer_road_diameter
    config.env["pixels_to_cars"] = 1.0 / config.env["cars_to_pixels"]

    config.env["speed_limit"] = 35
    config.env["drag"] = -0.1
    config.env["light_brakes_acceleration"] = -2.0
    config.env["heavy_brakes_acceleration"] = -15.0

    print("initializing cars...")
    config.env["cars"] = []
    car_count = 8
    car_speeds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    car_accelerations = [2.2, 1.4, 1.4, 1.9, 1.1, 0.9, 1.5, 1.5, 1.5, 1.5]
    car_variances = [5.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(car_count):
        location = i * (config.env["road_length"] / car_count)
        config.env["cars"].append(Car(i+1, config, location, car_speeds[i], car_accelerations[i], car_variances[i]))

    while True:
        loop(config)

def loop(config):
    dt = config.clock.tick(config.framerate)

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
        text_surface = config.font.render("Car " + str(car.label) + " speed: " + format(car.speed, ".2f"), True, BLACK)
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