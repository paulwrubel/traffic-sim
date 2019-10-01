import pygame
import math
from pygame import Surface, draw, Rect, transform
from pygame.math import Vector2
from constants import *

class Car:
    def __init__(self, label, config, location, speed = 0.0, acceleration = 1.0, speed_limit_variance = 0.0):
        self.env = config.env

        self.label = label
        self.location = location
        self.speed = speed
        self.acceleration_constant = acceleration
        self.acceleration = self.acceleration_constant
        self.speed_limit_variance = speed_limit_variance
        self.confortable_speed_limit = self.env["speed_limit"] + self.speed_limit_variance

        self.car_length = 1.0
        self.car_width = 0.5

        car_length_pixels = self.car_length * self.env["cars_to_pixels"]
        car_width_pixels = self.car_width * self.env["cars_to_pixels"]

        self.left_brake_light_rect = Rect((car_length_pixels * 0.9, car_width_pixels * 0.75), (car_length_pixels * 0.1, car_width_pixels * 0.25))
        self.right_brake_light_rect = Rect((car_length_pixels * 0.9, 0), (car_length_pixels * 0.1, car_width_pixels * 0.25))

        self.rect = Rect((0, 0), (car_length_pixels, car_width_pixels))
        self.original_surface = pygame.Surface((car_length_pixels, car_width_pixels), pygame.SRCALPHA)

        self.original_surface.fill(WHITE)
        draw.rect(self.original_surface, BLACK, self.rect, 3)

        text_surface = config.font.render(str(self.label), True, BLACK)
        self.original_surface.blit(text_surface, (5, 5))

        self.affected_surface = self.original_surface.copy()

    def update(self, config, dt):
        self.location += self.speed * dt
        self.location %= self.env["road_length"]

        self.speed += (self.env["drag"] + self.acceleration) * dt
        self.speed = max(self.speed, 0)

        self.acceleration, self.brakes = self.get_acceleration_and_brakes(dt)
        self.handle_crash(dt)

        self.update_surface(config)

    def get_acceleration_and_brakes(self, dt):
        next_car = self.car_after()

        if next_car is not None:
            # our front bumper to their rear bumper
            distance_from_next_car = self.distance_from(next_car)
            # positive if we are going faster
            speed_difference = self.speed - next_car.speed

            if distance_from_next_car < 2:
                if speed_difference > 0:
                    return self.env["max_braking_acceleration"], True
                else:
                    return self.env["max_braking_acceleration"] / 2.0, True

            if self.speed >= self.confortable_speed_limit:
                return self.confortable_speed_limit - self.speed, True

            acceleration = distance_from_next_car - 1.0
            return acceleration, acceleration < 0.0

            # if distance_from_next_car >= 2:
            #     if self.speed <= self.speed_limit:
            #         return self.acceleration_constant, False
            #     else:
            #         return self.env["drag"], False
            # # elif distance_from_next_car >= 1.5:
            # #     return self.env["coast_acceleration"]
            # elif distance_from_next_car >= 0.8:
            #     return self.env["light_brakes_acceleration"], True
            # else:
            #     return self.env["heavy_brakes_acceleration"], True
            
        else: # if we are the only car
            if self.speed <= self.speed_limit:
                self.acceleration = self.acceleration_constant
            else:
                self.acceleration = self.env["drag"]

    def handle_crash(self, dt):
        next_car = self.car_after()
        if next_car is not None and self.distance_from(next_car) <= 0:
            print("Car " + str(self.label) + " CRASHED into Car " + str(next_car.label))
            next_car_before_speed = next_car.speed
            before_speed = self.speed

            next_car.speed += (before_speed - next_car_before_speed) * 1.1
            next_car.location += next_car.speed * dt * 2
            self.location %= self.env["road_length"]

            self.speed -= (before_speed - next_car_before_speed) * 0.9

            return True
        else:
            return False

    def car_after(self):
        if len(self.env["cars"]) > 1:
            my_index = self.env["cars"].index(self)
            next_index = (my_index + 1) % len(self.env["cars"])
            return self.env["cars"][next_index]
        else:
            return None

    def distance_from(self, other_car):
        if other_car is None:
            return None
        else:
            if other_car.location < self.location:
                other_car_loc = other_car.location + self.env["road_length"]
            else:
                other_car_loc = other_car.location

            return other_car_loc - self.location - ((self.car_length / 2.0) + (other_car.car_length / 2.0))

    def update_surface(self, config):
        self.affected_surface = self.original_surface.copy()

        if self.brakes:
            draw.rect(self.affected_surface, RED, self.left_brake_light_rect)
            draw.rect(self.affected_surface, RED, self.right_brake_light_rect)

        degrees_to_rotate = ((self.location / config.env["road_length"]) * 360)

        self.rotated_surface = transform.rotate(self.affected_surface, degrees_to_rotate)

        road_radius_pixels = ((config.env["road_length"] / math.pi) * 0.5) * config.env["cars_to_pixels"]

        x = -1.0 * road_radius_pixels * math.cos(math.radians(degrees_to_rotate-90))
        y = road_radius_pixels * math.sin(math.radians(degrees_to_rotate-90))

        self.true_center = Vector2(x, y)
        self.true_rect = Vector2(x - self.rotated_surface.get_bounding_rect().width/2, y - self.rotated_surface.get_bounding_rect().height/2)

    def draw(self, config):
        config.screen.blit(self.rotated_surface, config.center + self.true_rect)

