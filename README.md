# AI Traffic Light Simulation

An interactive Pygame-based traffic simulation that uses a pre-trained XGBoost model to decide whether pedestrians or vehicles should get priority at a traffic light. The simulation models a vertical road with cars moving upward and pedestrians crossing horizontally. The AI model predicts the optimal priority every 15 seconds based on current traffic conditions.

---

## Overview

This project simulates a single-lane road controlled by a traffic light. Cars spawn from the bottom and move upward; pedestrians spawn from the left or right side and cross the road. A machine learning model (`ratioAI.pkl`) analyses the current state (distance of first car to light, its speed, weather, temperature, number of waiting cars, and number of waiting pedestrians) and predicts whether people or cars should be given priority. The traffic light then changes accordingly, provided the intersection is clear.

The simulation also visualises the model’s confidence as priority bars and displays various statistics such as car count, people count, car:people ratio, time since last light change, temperature, weather, hour, day of week, and more.

---

## Features

- Real-time traffic and pedestrian simulation with acceleration/deceleration logic.
- AI-based traffic light control using an XGBoost regressor.
- Interactive controls to spawn cars/people, change weather, temperature, and manually control the traffic light.
- Visual indicators for priority (people vs. cars) and distances.
- Loads scenarios from a pre-recorded dataset (`data.pkl`) by row number.
- Supports extreme weather and temperature adjustments.

---
## Simulation Logic

- Cars spawn at the bottom, accelerate to a random speed (11–17 m/s by default), and move upward when the light allows. They decelerate if they approach another car or if the light is red/yellow.
- Pedestrians spawn on the left or right side and move horizontally. They cross when the car light is red (or when no cars are in the traffic region). They stop if the car light is green and they are near the crossing.
- Traffic Light starts red. Every 15 seconds, if movement is enabled, the program calls the AI model with the current state. The model returns a value between 0 and 1, interpreted as the probability that people should go first. If the result is ≥ 0.5, the light turns red (people first); otherwise, it turns green (cars first). The light only changes if the corresponding traffic region (cars or people) is clear.
- Traffic Region: A rectangular area around the light used to prevent switching while vehicles or pedestrians are still crossing.

## File Descriptions

| File | Description |
|------|-------------|
| `app_2.py` | Main program: initialises Pygame, loads model and data, runs the main loop, handles input, and controls the traffic light via AI. |
| `constants.py` | Global constants: screen size, colours, speeds, acceleration, pixel-to-metre conversion, light timings, etc. |
| `car.py` | `Car` class: speed, acceleration, deceleration, movement, distance calculation, and drawing. |
| `person.py` | `Person` class: pedestrian movement and drawing. |
| `road.py` | `Road` class: manages cars, people, traffic lights, spawning, updating, drawing, and priority logic. |
| `interactions.py` | `TrafficLight` and `TrafficLightStatus` classes. Defines light colours and deceleration behaviour. |
| `ratioAI.pkl` | Pickled XGBoost regressor model. Input features: `[distance, first_speed, extreme_weather, temperature, num_waiting_cars, num_waiting_people]`. Output: a float used as people-first probability. |
| `data.pkl` | Pickled dataset with arrays for distance, first speed, extreme weather, temperature, waiting cars, waiting people, and expected `people_first` result. |

## Controls

The simulation is controlled entirely via the keyboard. The following keys (buttons) are available:

| Key | Action |
|-----|--------|
| **↓ (Down Arrow)** | Spawn a car at the bottom of the road. |
| **← (Left Arrow)** | Spawn a pedestrian on the left side. |
| **→ (Right Arrow)** | Spawn a pedestrian on the right side. |
| **Space** | Toggle simulation movement (pause / resume). When paused, cars and people stop moving. |
| **1** | Change the traffic light to **RED** (people first). *Only works when the simulation is in its initial reset state.* |
| **2** | Change the traffic light to **GREEN** (cars first). *Only works when the simulation is in its initial reset state.* |
| **3** | Set **extreme weather** to `True` and adjust the predicted traffic volume to 632. |
| **4** | Set **extreme weather** to `False` and adjust the predicted traffic volume to 828. |
| **5** | Increase temperature by 1°C. |
| **6** | Decrease temperature by 1°C. |
| **Backspace** | Reset the simulation (clears all cars and people, resets light to red, sets `resetted = True`, temperature to 20°C, extreme weather to `False`, and traffic volume prediction to 828). |

**Important notes about keys `1` and `2`:**  
They only work when `main_road.resetted` is `True`. This is the case at the very beginning and immediately after pressing `Backspace`. Once you press `Space` to start the simulation, `resetted` becomes `False`, and keys `1` and `2` will no longer change the light. To use them again, reset the simulation with `Backspace`.

## Requirements

- Python 3.8+
- pygame
- numpy
- pandas
- scikit-learn
- xgboost
- pickle (standard library)

Install the dependencies with:

```bash
pip install pygame numpy pandas scikit-learn xgboost
