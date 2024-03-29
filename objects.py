import pygame
import math
from pygame import Surface, draw, Rect, transform
from pygame.math import Vector2
from constants import *

class Car:
    def __init__(self, label, config, location, speed = 0.0, acceleration = 1.0, speed_limit_variance = 0.0):
        self.label = label
        self.location = location
        self.speed = speed
        self.acceleration_constant = acceleration
        self.acceleration = self.acceleration_constant
        self.speed_limit_variance = speed_limit_variance
        self.speed_limit = config.speed_limit + self.speed_limit_variance

        self.car_length = 1.0
        self.car_width = 0.5

        car_length_pixels = self.car_length * config.cars_to_pixels
        car_width_pixels = self.car_width * config.cars_to_pixels

        self.left_brake_light_rect = Rect((car_length_pixels * 0.9, car_width_pixels * 0.75), (car_length_pixels * 0.1, car_width_pixels * 0.25))
        self.right_brake_light_rect = Rect((car_length_pixels * 0.9, 0), (car_length_pixels * 0.1, car_width_pixels * 0.25))

        self.rect = Rect((0, 0), (car_length_pixels, car_width_pixels))
        self.original_surface = pygame.Surface((car_length_pixels, car_width_pixels), pygame.SRCALPHA)

        self.original_surface.fill(WHITE)
        draw.rect(self.original_surface, BLACK, self.rect, 3)

        text_surface = config.font.render(str(self.label), True, BLACK)
        self.original_surface.blit(text_surface, (5, 5))

        self.affected_surface = self.original_surface.copy()

    def update(self, config, dt, cars):
        self.location += 0.0001 * self.speed * dt
        self.location %= config.road_length

        self.brakes = False

        self.speed += 0.001 * self.acceleration * dt

        if self.speed < 0:
            self.speed = 0

        if len(cars) > 1:
            car_after = cars[(cars.index(self) + 1) % len(cars)]
            if car_after.location < self.location:
                car_after_loc = car_after.location + config.road_length
            else:
                car_after_loc = car_after.location

            diff = (car_after_loc - self.location) - 1

            dist_coefficient = 0.3 # 0.2 + (self.speed / 15.0)

            if diff >= dist_coefficient * 2:
                if self.speed <= self.speed_limit:
                    self.acceleration = self.acceleration_constant
                else:
                    self.acceleration = config.coast_acceleration
            # elif diff >= dist_coefficient * 1.5:
            #     self.acceleration = config.coast_acceleration
            elif diff >= dist_coefficient * 0.8:
                self.acceleration = config.light_brakes_acceleration
            else:
                self.acceleration = config.heavy_brakes_acceleration

            if diff <= 0:
                print("Car " + str(self.label) + " CRASHED into Car " + str(car_after.label))
                car_after.speed += self.speed * 0.9
                car_after.location += 0.0002 * car_after.speed * dt
                self.speed = 0

        else:
            if self.speed <= self.speed_limit:
                self.acceleration = self.acceleration_constant
            else:
                self.acceleration = config.drag

        self.update_surface(config)

    # def get_acceleration(self, config):
        


    def update_surface(self, config):
        self.affected_surface = self.original_surface.copy()

        if self.brakes:
            draw.rect(self.affected_surface, RED, self.left_brake_light_rect)
            draw.rect(self.affected_surface, RED, self.right_brake_light_rect)

        degrees_to_rotate = ((self.location / config.road_length) * 360)

        self.rotated_surface = transform.rotate(self.affected_surface, degrees_to_rotate)

        road_radius_pixels = ((config.road_length / math.pi) * 0.5) * config.cars_to_pixels

        x = -1.0 * road_radius_pixels * math.cos(math.radians(degrees_to_rotate-90))
        y = road_radius_pixels * math.sin(math.radians(degrees_to_rotate-90))

        self.true_center = Vector2(x, y)
        self.true_rect = Vector2(x - self.rotated_surface.get_bounding_rect().width/2, y - self.rotated_surface.get_bounding_rect().height/2)

    def draw(self, config):
        config.screen.blit(self.rotated_surface, config.center + self.true_rect)

