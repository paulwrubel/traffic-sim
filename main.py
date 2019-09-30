import sys, pygame
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
    framerate = 60
    config = Config(screen_size, framerate)
    config.clock = time.Clock()
    config.screen = display.set_mode(config.size, config.flags)
    config.font = font.SysFont("arial", 20)

    print("initializing road...")
    config.road_length = 20
    config.road_width = 1
    config.road_true_width = int(2.2 * config.height / config.road_length)
    config.road_true_outer_radius = int((config.height / 2) * 0.9)
    config.road_true_inner_radius = config.road_true_outer_radius - config.road_true_width
    config.road_true_radius = int((config.road_true_outer_radius + config.road_true_inner_radius) / 2.0)

    config.speed_limit = 35
    config.coast_acceleration = -0.1
    config.light_brakes_acceleration = -2.0
    config.heavy_brakes_acceleration = -15.0

    print("initializing cars...")
    cars = []
    car_count = 8
    car_speeds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    car_accelerations = [2.2, 1.4, 1.4, 1.9, 1.1, 0.9, 1.5, 1.5, 1.5, 1.5]
    car_variances = [5.0, -2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(car_count):
        location = i * (config.road_length / car_count)
        cars.append(Car(i+1, config, location, car_speeds[i], car_accelerations[i], car_variances[i]))

    while True:
        loop(config, cars)

def loop(config, cars):
    dt = config.clock.tick(config.framerate)

    check_events(config)
    config.screen.fill(WHITE)

    draw.circle(config.screen, BLACK, config.center, config.road_true_outer_radius, 2)
    draw.circle(config.screen, BLACK, config.center, config.road_true_inner_radius, 2)
    draw.circle(config.screen, BLACK, config.center, 10)
    for car in cars:
        car.update(config, dt, cars)
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