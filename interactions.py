from constants import *

import enum
import time

import pygame
from pygame import Rect

from car import Car

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)


class CarMutator:
    def mutate(self, car: Car) -> bool:
        raise NotImplementedError


class RoadObject():
    y: int

    def __init__(self, y):
        self.y = y

    def draw(self, road, window: pygame.Surface, font: pygame.font.Font) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError


class TrafficLightStatus(enum.Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


class TrafficLight(RoadObject):
    status: TrafficLightStatus
    time_transition: int  # Time until transitioning to next status
    _last_updated: float

    def __init__(self, y):
        super().__init__(y)
        self.status = TrafficLightStatus.red

    def change_to_red(self):
        self.status = TrafficLightStatus.red
    
    def change_to_yellow(self):
        self.status = TrafficLightStatus.yellow
    
    def change_to_green(self):
        self.status = TrafficLightStatus.green

    def mutate(self, car: Car) -> bool:
        if self.status != TrafficLightStatus.green and car.speed > 0:
            car.decelerate()
            return True
        return False

    def draw(self, road, window: pygame.Surface, font: pygame.font.Font):
        rect = Rect(road.spawn_coords[0] - 100, self.y, 200, 100)
        pygame.draw.rect(window, {
            TrafficLightStatus.green: TRAFFIC_LIGHT_GREEN,
            TrafficLightStatus.yellow: TRAFFIC_LIGHT_YELLOW,
            TrafficLightStatus.red: TRAFFIC_LIGHT_RED
        }[self.status], rect)

