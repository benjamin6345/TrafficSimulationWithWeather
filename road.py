import time

from car import Car
from constants import *
import pygame
import numpy as np
import pandas as pd
from interactions import *
from person import *
import random
import math
from copy import deepcopy

pygame.font.init()
font = pygame.font.Font(None, 36)


class Road:
    cars: list[Car]
    rect: pygame.Rect
    spawn_coords: tuple[int, int]
    last_updated: float
    people: list[Person]
    objects: list[TrafficLight]
    export_finished = 0
    export_speeds = []
    export_distances = []

    def __init__(self, x: int, objects, mutations, target_num_car, target_num_people):
        self.cars = []
        self.objects = objects
        self.mutations = mutations
        self.rect = pygame.Rect(x, 0, 200, HEIGHT)
        self.spawn_coords = (x + 100, HEIGHT - 50)
        self.last_updated = time.time()
        self.num_waiting_cars = 0
        self.x = x
        self.people = []
        self.left_num_waiting_people = 0
        self.right_num_waiting_people = 0
        self.traffic_light_x, self.traffic_light_y = self.spawn_coords[0] - 100, self.objects[0].y
        self.can_move = False
        
        self.removed_car = set()
        self.removed_people = set()
        
        self.traffic_light_width = 200
        self.traffic_light_height = 100
        
        self.detect_region_x = self.traffic_light_x
        self.detect_region_y = self.traffic_light_y+100
        self.detect_region_width = 200
        self.detect_region_height = 150
        
        self.line_break_car = None
        
        self.model_result = None
        
        self.resetted = False
        
    
    def dist_of_first_car_from_light(self):
        for car in self.cars:
            if car not in self.removed_car:
                car_x, car_y = car.position
                light_y = self.objects[0].y
                if car_y >= light_y:
                    dist_pixel = abs(car_y-light_y)
                    dist_m = dist_pixel/PIXEL_PER_METRE
                    return dist_m
                
    def speed_of_first_car(self):
        for car in self.cars:
            if car not in self.removed_car:
                car_x, car_y = car.position
                light_y = self.objects[0].y
                
                if car_y >= light_y:
                    return car.speed
                
                
    def add_car(self, car: Car) -> None:
        self.cars.append(car)

    def spawn_car(self, speed=None) -> Car:
        if speed is None:
            speed = random.uniform(11, 17)
        car = Car(self.spawn_coords, speed, speed)
        
        self.cars.append(car)
        self.num_waiting_cars += 1
        
        return car
    
    def spawn_person(self, side:str) -> Person:
        person = Person(side)
        
        person_y = self.traffic_light_y + random.randint(1, 100)
        if side == 'left':
            person.position = (0, person_y)
            self.left_num_waiting_people += 1
        elif side == 'right':
            person.position = (WIDTH, person_y)
            self.right_num_waiting_people += 1
        self.people.append(person)
    
    def draw_people_car_priority(self, window):
        #People rect
        if self.model_result is None:
            p_color = BLACK
            c_color = BLACK
            p_value = 0
            c_value = 0
            
        else:
            p_value = self.model_result
            c_value = 1-self.model_result
            p_color = GREEN if p_value >= 0.5 else RED
            c_color = RED if p_color == GREEN else GREEN
            
            
        if self.model_result:
            p_rect_height = int(PRIORITY_RECT_MAX_HEIGHT * self.model_result)
            
        else:
            p_rect_height = 10
            
        p_left = P_X
        p_top = BOTTOM_Y - p_rect_height
        p_width = PRIORITY_RECT_WIDTH
        p_height = p_rect_height
        people_text = font.render('People', True, p_color)
        people_percentage_text = font.render(f'{round(100*p_value, 1)}%', True, p_color)
        people_rect = pygame.Rect(p_left, p_top, p_width, p_height)
        
        #Car rect
        if self.model_result:
            c_rect_height = int(PRIORITY_RECT_MAX_HEIGHT - p_rect_height)
        else:
            c_rect_height = 10
        
        c_left = C_X
        c_top = BOTTOM_Y - c_rect_height
        c_width = PRIORITY_RECT_WIDTH
        c_height = c_rect_height
        car_text = font.render('Car', True, c_color)
        car_percentage_text = font.render(f'{round(100*c_value, 1)}%', True, c_color)
        car_rect = pygame.Rect(c_left, c_top, c_width, c_height)
        
        
        if self.resetted:
            c_color = BLACK
            p_color = BLACK
        
        pygame.draw.rect(window, p_color, people_rect)
        pygame.draw.rect(window, c_color, car_rect)
        window.blit(people_text, (p_left, p_top-50))
        window.blit(people_percentage_text, (p_left, p_top+p_height+30))
        window.blit(car_text, (c_left, c_top-50))
        window.blit(car_percentage_text, (c_left, c_top+c_height+30))
    
            
    def draw_distance(self, window, font:pygame.font.Font):
        light_bottom_y = self.objects[0].y+100
        for car in self.cars:
            car_x, car_y = car.position
            if car not in self.removed_car and car_y > light_bottom_y:
                
                dist_pixel = abs(light_bottom_y-car_y)
                dist_m = dist_pixel/PIXEL_PER_METRE
                dist_text = font.render(f'{int(dist_m)}m', True, YELLOW)
                text_y = int((light_bottom_y+car_y)/2)
                text_x = car_x+20
                window.blit(dist_text, (text_x, text_y))
                pygame.draw.line(window, YELLOW, (car_x, light_bottom_y), (car_x, car_y))
                break

    def draw(self, window: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(window, ROAD_COLOR, self.rect)
        for object in self.objects:
            object.draw(self, window, font)
        for car in self.cars:
            car.draw(window)
        for person in self.people:
            if person not in self.removed_people:
                person.draw(window)

        self.draw_people_car_priority(window)
        self.draw_distance(window, font)
        
        
                
    def obj_pos_within_light(self, obj):
        if isinstance(obj, Car):
            car_x, car_y = obj.position
            if car_y >= self.traffic_light_y and car_y <= self.traffic_light_y+self.traffic_light_height:
                return True
            else:
                return False
        
        if isinstance(obj, Person):
            person_x, person_y = obj.position
            if person_x >= self.traffic_light_x and person_x <= self.traffic_light_x+self.traffic_light_width:
                return True
            else:
                return False
               
    def traffic_region_have_car(self):
        for car in self.cars:
            if car not in self.removed_car:
                if self.obj_pos_within_light(car):
                    return True
                
        return False
            
    
    def traffic_region_have_people(self):
        for person in self.people:
            if person not in self.removed_people:
                if self.obj_pos_within_light(person):
                    return True
                
        return False
    
    def have_people_close_in_front(self, person:Person):
        main_x, main_y = person.position
        
        for temp_person in self.people:
            if not temp_person.side == person.side: continue
            temp_x, temp_y = temp_person.position
            dist = math.dist((main_x, main_y), (temp_x, temp_y))
            
            
            if dist <= 15:
                if person.side == 'left':
                    if temp_x > main_x:
                        return True

                if person.side == 'right':
                    if temp_x < main_x:
                        return True
        
        return False
    

    
    def have_car_close_in_front(self, car:Car):
        main_x, main_y = car.position
        for temp_car in self.cars:
            temp_x, temp_y = temp_car.position
            dist = math.dist((main_x, main_y), (temp_x, temp_y))
            
            if dist <= 40 and temp_y < main_y:
                return True
        
        return False

            
    def update(self) -> None:
        to_export = False
        if time.time() - self.last_updated >= 5:
            to_export = True
            self.last_updated = time.time()

        for obj in self.objects:
            try:
                obj.update()
                
            except:
                pass
        
        
            
        for i in range(len(self.cars)):
            car = self.cars[i]
            
            car_x, car_y = car.position
            
            chain_mutated = False
            # Calculate chain effect for this car if it's behind other cars
            if i != 0:
                front = self.cars[i - 1]
                distance = car.distance_to(front)
                if to_export:
                    self.export_distances.append(distance)
                if distance <= DEC_LOWER_BOUND_DIST and car.speed > 0:
                    car.decelerate()
                    chain_mutated = True
                elif car.speed == car.max_speed or car.speed == 0:
                    # Stop accelerating/decelerating if cannot go further
                    car.accelerating = False
                    car.decelerating = False

            obj_mutated = False
            if not chain_mutated:  # Chain effect mutation takes precedence over object mutations
                for obj in self.objects:
                    if isinstance(obj, TrafficLight):
                        if abs(car.position[1] - obj.y) <= DEC_LOWER_BOUND_DIST+80 and car.position[1] > obj.y:
                            obj_mutated = obj.mutate(car)
                            break  # Only mutate by one object
                        
                    else:
                        if abs(car.position[1] - obj.y) <= DEC_LOWER_BOUND_DIST+140:
                            obj_mutated = obj.mutate(car)
                            break  # Only mutate by one object
                if car.manual_decelerate:
                    # A special case, where we manually decelerate cars if requested
                    if car.speed > 0:
                        car.decelerate()
                        obj_mutated = True
                    else:
                        car.manual_decelerate = False

            if not chain_mutated and not obj_mutated and car.speed < car.max_speed:
                car.accelerate()
            
            if self.can_move:
                car.move()
                
            car_y = car.position[1]
            if car_y < self.objects[0].y+50 and car not in self.removed_car:
                self.num_waiting_cars -= 1
                self.removed_car.add(car)
            car.prev_updated_time = time.time()
            
            
                
        for person in self.people:
            person_x, person_y = person.position
            
            if person.side == 'right' and person not in self.removed_people:
                if self.can_move and self.obj_pos_within_light(person):
                    person.move()
                
                
                elif self.can_move and not (self.have_people_close_in_front(person)): 
                    
                    #If light is not green for car, or maybe if the person is far away from light, keep moving
                    if self.objects[0].status == TrafficLightStatus.green:
                        if person_x <= self.traffic_light_x+self.traffic_light_width+20 and not self.obj_pos_within_light(person): #If is green light for car: stop moving
                            pass
                        
                        else:
                            person.move()
                            
                    else:
                        if not self.traffic_region_have_car():
                            person.move()
    
                if person_x < self.traffic_light_x:
                    self.right_num_waiting_people -= 1
                    self.removed_people.add(person)
                    
            if person.side == 'left' and person not in self.removed_people:
                if self.can_move and self.obj_pos_within_light(person):
                    person.move()
                    
                elif self.can_move and not (self.have_people_close_in_front(person)): 
                    #If light is not green for car, or maybe if the person is far away from light, keep moving
                    if self.objects[0].status == TrafficLightStatus.green:
                        if person_x >= self.traffic_light_x-20 and not self.obj_pos_within_light(person): #If is green light for car: stop moving
                            pass #Cannot move
                        
                        else:
                            
                            person.move()
                            
                    else:
                        if not self.traffic_region_have_car():
                            person.move()
                        
                        
                if person_x >= self.traffic_light_x+200:
                    self.left_num_waiting_people -= 1
                    self.removed_people.add(person)
                    
                

            
    def reset(self):
        self.cars = []
        self.people = []
        self.num_waiting_cars = 0
        self.left_num_waiting_people = 0
        self.right_num_waiting_people = 0
        self.objects[0].status = TrafficLightStatus.red
        self.can_move = False
        
    def return_ratio(self):
        num_cars = self.num_waiting_cars
        num_people = self.left_num_waiting_people + self.right_num_waiting_people

        try:
            return round(num_cars/num_people, 2)
        except ZeroDivisionError:
            return math.inf
        
        
    def detect_line_break_car(self):
        for i, car in enumerate(self.cars):
            if i == 0: continue
            if car not in self.removed_car and self.cars[i-1] not in self.removed_car:
                temp_car_x, temp_car_y = self.cars[i-1].position
                dist = car.distance_to(self.cars[i-1])
                if dist >= 100:
                    #and temp_car_y <= (self.detect_region_y+self.detect_region_height) and temp_car_y >= self.detect_region_y and not self.line_break_pos

                    return self.cars[i-1]
                
        return True
    
    
    def line_break_passed_light(self, car:Car):
        car_x, car_y = car.position
        
        return car_y <= self.traffic_light_y-10
    

    