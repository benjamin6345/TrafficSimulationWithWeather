#輸入data.xlsx行數，自動設置場景
from constants import *
from interactions import *
from road import Road

import pygame
import time
import pickle
import numpy as np

import pandas as pd
import numpy as np
import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
# from tensorflow.keras.models import Sequential # type: ignore
# from tensorflow.keras.layers import Dense, LSTM # type: ignore
# from tensorflow.keras.models import load_model # type: ignore


pygame.init()
pygame.font.init()


window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("速度计算模拟程式")
font = pygame.font.Font(None, 36)


with open('ratioAI.pkl', 'rb') as file:
    model = pickle.load(file)
#
with open('data.pkl', 'rb') as file:
    data = pickle.load(file)
    
row_num = int(input('Input row num: '))

data_dist = data['distance'][row_num]
data_speed = data['first_speed'][row_num]
data_extreme_weather = data['extreme_weather'][row_num]
data_temperature = data['temperature'][row_num]
data_num_waiting_car = data['num_waiting_cars'][row_num]
data_num_waiting_people = data['num_waiting_people'][row_num]
data_result = data['people_first'][row_num]

roads = [
    Road(300, [
        TrafficLight(TRAFFIC_LIGHT_Y),
    ], [], data_num_waiting_car, data_num_waiting_people)
]


if __name__ == "__main__":
    clock = pygame.time.Clock()
    pressed = False
    cooldown = 0
    last_exported = time.time()

    last_light_turned_time = time.time()
    just_started = True
    
    main_road = roads[0]
    countdown = None
    previously_tapped_key = None
    
    main_road.resetted = True
    line_break_car = None
    
    extreme_weather = data_extreme_weather
    if extreme_weather == True:
        weather = 1
    else:
        weather = 0
    
    temperature = data_temperature
    spawn_person_time = 0
    
    
    traffic_volume_prediction = 828
        
    predicted_traffic = None
    current_hour = None
    
    while True:
        clock.tick(FPS)
        
        if main_road.objects[0].status == TrafficLightStatus.red: #show車先
            if main_road.num_waiting_cars < data_num_waiting_car:
                speed = None
                
                if countdown is not None and 15-countdown <= 5: #Only spawn when there is 5 sec left
                    speed = ((HEIGHT-(TRAFFIC_LIGHT_Y+100))/PIXEL_PER_METRE-data_dist)/5-3
                    
                    main_road.spawn_car(speed)
                    
        else:
            while main_road.num_waiting_cars < data_num_waiting_car: #show人先
                speed = None
                if countdown is not None and 15-countdown <= 5: #Keep spawning, but if it is 5 sec left, then spawn with right speed
                    speed = data_dist/5
                main_road.spawn_car(speed)
        
        if main_road.left_num_waiting_people + main_road.right_num_waiting_people < data_num_waiting_people:
            if time.time()-spawn_person_time >= 0.1:
                main_road.spawn_person('left')
                spawn_person_time = time.time()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN and not pressed and time.time() - cooldown >= 0:
                cooldown = time.time()
                if event.key == pygame.K_DOWN:  # 按下指着左边的箭头，在左边生成车子
                    main_road.spawn_car()
                    previously_tapped_key = 'Down'
                    
                if event.key == pygame.K_LEFT:
                    main_road.spawn_person('left')
                    previously_tapped_key = 'Left'
                    
                if event.key == pygame.K_RIGHT:
                    main_road.spawn_person('right')
                    previously_tapped_key = 'Right'
                    
                if event.key == pygame.K_SPACE:
                    main_road.can_move = True if main_road.can_move == False else False
                    previously_tapped_key = 'Space'
                    if main_road.can_move and main_road.resetted:
                        last_light_turned_time = time.time()
                    main_road.resetted = False
                    
                if event.key == pygame.K_1 and main_road.resetted:
                    main_road.objects[0].change_to_red()
                    previously_tapped_key = '1'
                    
                if event.key == pygame.K_2 and main_road.resetted:
                    main_road.objects[0].change_to_green()
                    previously_tapped_key = '2'
                    
                if event.key == pygame.K_BACKSPACE:
                    main_road.reset()
                    just_started = True
                    previously_tapped_key = 'Backspace'
                    main_road.resetted = True
                    countdown = 0
                    temperature = 20
                    extreme_weather = False
                    weather = 0
                    traffic_volume_prediction = 828
                    
                if event.key == pygame.K_3:
                    extreme_weather = True
                    weather = 1 
                    traffic_volume_prediction = 632
                    
                if event.key == pygame.K_4:
                    extreme_weather = False
                    weather = 0
                    traffic_volume_prediction = 828
                    
                if event.key == pygame.K_5:
                    temperature += 1
                    
                if event.key == pygame.K_6:
                    temperature -= 1
                    


            # 避免一次性检测到太多次按键（按了一下，就只触发事件一次）
            elif event.type == pygame.KEYUP:
                pressed = False
        
        num_cars = len(main_road.cars)
        

        window.fill(BACKGROUND_COLOR)
        for road in roads:
            road.update()
            road.draw(window, font)
                
        
        car_people_ratio = main_road.return_ratio()
        people_text = font.render(f'People: {main_road.left_num_waiting_people + main_road.right_num_waiting_people}', True, (0, 0, 0))
        car_text = font.render(f'Car: {main_road.num_waiting_cars}', True, (0, 0, 0))
        ratio_text = font.render(f'Car:People = {car_people_ratio}', True, (0, 0, 0))
        
        if main_road.can_move:
            countdown = round(time.time()-last_light_turned_time, 2)
        
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        day_of_week = current_time.weekday()
        is_holiday = np.where((day_of_week == 5) | (day_of_week == 6), 1, 0)
        is_holiday_true_false = np.where((day_of_week == 5) | (day_of_week == 6), True, False)
            
        countdown_text = font.render(f'Same light time: {countdown}', True, (0, 0, 0))
        

        weather_text = font.render(f'Extreme weather: {extreme_weather}', True, (0, 0, 0))
        temperature_text = font.render(f'Temperature: {temperature}°C', True, (0, 0, 0))
        
        traffic_volume_prediction_text = font.render(f'PTV: {traffic_volume_prediction}', True, (0, 0, 0))
        hour_text = font.render(f"hour: {current_hour}", True, (0, 0, 0))
        day_of_week_text = font.render(f"day_of_week: {day_of_week}", True, (0, 0, 0))
        is_holiday_text = font.render(f"is_holiday: {is_holiday_true_false}", True, (0, 0, 0))
        
        window.blit(car_text, (0, 0))
        window.blit(people_text, (0, 50))
        window.blit(ratio_text, (0, 100))
        window.blit(countdown_text, (550, 50))
        window.blit(weather_text, (0, 150))
        window.blit(temperature_text, (0, 200))
        window.blit(hour_text, (0, 250))
        window.blit(day_of_week_text, (0, 300))
        window.blit(is_holiday_text,(0, 350))
        window.blit(traffic_volume_prediction_text, (0, 400))
        
        
        if main_road.can_move and (time.time()-last_light_turned_time >= 15):
            #Data preparation
            dist = data_dist
            speed = data_speed
            extreme_weather = True
            num_waiting_people = main_road.left_num_waiting_people + main_road.right_num_waiting_people
            num_waiting_car = main_road.num_waiting_cars       
            
            
            if main_road.num_waiting_cars == 0:
                dist = -1
                speed = -1
                
            data = np.array([dist, speed, extreme_weather, temperature, num_waiting_people, num_waiting_people])
            result = model.predict([data])[0]
            
            main_road.model_result = result
            
            
            
            if round(result) == 1 and not main_road.traffic_region_have_car(): #People First (Green to red)
                if main_road.objects[0].status == TrafficLightStatus.green:
                    last_light_turned_time = time.time()
                main_road.objects[0].change_to_red()
                
                
            else: #Car First
                if main_road.objects[0].status == TrafficLightStatus.red and not main_road.traffic_region_have_people(): #Red to green
                    last_light_turned_time = time.time()
                main_road.objects[0].change_to_green()
                
            just_started = False
        

        pygame.display.update()