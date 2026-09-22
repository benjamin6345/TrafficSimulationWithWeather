# AI Traffic Light Simulation

> **Main entry point:** `app_2.py` — use this file as `main.py`.

---

## Overview

This project is a **Pygame-based traffic simulation** that uses a pre-trained **XGBoost model** to decide whether pedestrians or vehicles should get priority at a traffic light.

The simulation models a single vertical road:

- **Cars** spawn from the bottom and move upward.
- **Pedestrians** spawn from the left or right and cross horizontally.
- A **traffic light** controls whether cars or people can move.
- The AI model predicts the optimal priority every **15 seconds** based on current traffic conditions.

The model is loaded from `ratioAI.pkl`, and scenarios are loaded from `data.pkl`.

---

## Main Entry Point

`app_2.py` is the main program. You can run it directly or rename it to `main.py`.

```bash
python app_2.py
```

Or:

```bash
cp app_2.py main.py
python main.py
```

When started, it asks for a row number from the dataset:

```text
Input row num:
```

Enter a valid row index from `data.pkl` to select a scenario.

---

## Project Structure

| File | Description |
|------|-------------|
| `app_2.py` | Main program: initialises Pygame, loads model and data, runs the main loop, handles input, and controls the traffic light via AI. |
| `constants.py` | Global constants: screen size, colours, speeds, acceleration, pixel-to-metre conversion, light timings, etc. |
| `car.py` | `Car` class: speed, acceleration, deceleration, movement, distance calculation, and drawing. |
| `person.py` | `Person` class: pedestrian movement and drawing. |
| `road.py` | `Road` class: manages cars, people, traffic lights, spawning, updating, drawing, and priority logic. |
| `interactions.py` | `TrafficLight` and `TrafficLightStatus` classes. Defines light colours and deceleration behaviour. |
| `ratioAI.pkl` | Pickled XGBoost regressor model. |
| `data.pkl` | Pickled dataset with scenario rows. |
| `requirements.txt` | Python dependencies. |
| `README.md` | Project documentation. |

---

## Simulation Logic

### Cars

- Spawn at the bottom of the road.
- Accelerate to a random speed by default, usually between **11–17 m/s**.
- Move upward when the light allows.
- Decelerate if they approach another car or if the light is red/yellow.
- Are removed from the waiting count when they pass the traffic light.

### Pedestrians

- Spawn on the left or right side of the road.
- Move horizontally across the road.
- Cross when the car light is red, or when no cars are in the traffic region.
- Stop if the car light is green and they are near the crossing.

### Traffic Light

- Starts as **red**.
- Every **15 seconds**, if movement is enabled, the program calls the AI model.
- The model returns a value between `0` and `1`, interpreted as the probability that people should go first.
- If `round(result) == 1`, the light turns **red** (people first).
- Otherwise, the light turns **green** (cars first).
- The light only changes if the corresponding traffic region is clear.

### Traffic Region

A rectangular area around the light used to prevent switching while vehicles or pedestrians are still crossing.

```python
self.traffic_light_x = self.spawn_coords[0] - 100
self.traffic_light_y = self.objects[0].y
self.traffic_light_width = 200
self.traffic_light_height = 100
```

---

## AI Traffic Light Control

The model input features are intended to be:

```python
[distance, first_speed, extreme_weather, temperature, num_waiting_cars, num_waiting_people]
```

The output is a float used as the people-first probability.

In `app_2.py`, the prediction block looks like this:

```python
data = np.array([
    dist,
    speed,
    extreme_weather,
    temperature,
    num_waiting_people,
    num_waiting_people
])
result = model.predict([data])[0]
```

> **Note:** There may be a bug here. The last feature should likely be `num_waiting_car`, not `num_waiting_people`. Also, `extreme_weather` is hardcoded to `True` in this block, while the scenario value may be different.

---

## Controls

| Key | Action |
|-----|--------|
| **↓ Down Arrow** | Spawn a car at the bottom of the road. |
| **← Left Arrow** | Spawn a pedestrian on the left side. |
| **→ Right Arrow** | Spawn a pedestrian on the right side. |
| **Space** | Toggle simulation movement: pause / resume. |
| **1** | Change the traffic light to **RED** (people first). Only works when `main_road.resetted` is `True`. |
| **2** | Change the traffic light to **GREEN** (cars first). Only works when `main_road.resetted` is `True`. |
| **3** | Set **extreme weather** to `True` and adjust predicted traffic volume to `632`. |
| **4** | Set **extreme weather** to `False` and adjust predicted traffic volume to `828`. |
| **5** | Increase temperature by `1°C`. |
| **6** | Decrease temperature by `1°C`. |
| **Backspace** | Reset the simulation. |

### Important note about keys `1` and `2`

Keys `1` and `2` only work when `main_road.resetted` is `True`.  
This is the case at the very beginning and immediately after pressing **Backspace**.  
Once you press **Space** to start the simulation, `resetted` becomes `False`, and keys `1` and `2` will no longer change the light.  
To use them again, reset the simulation with **Backspace**.

---

## Requirements

- Python 3.8+
- pygame
- numpy
- pandas
- scikit-learn
- xgboost
- pickle (standard library)

Install dependencies:

```bash
pip install pygame numpy pandas scikit-learn xgboost
```

---

## How to Run

1. Install the dependencies:

   ```bash
   pip install pygame numpy pandas scikit-learn xgboost
   ```

2. Make sure these files are in the same directory:

   - `app_2.py`
   - `constants.py`
   - `car.py`
   - `person.py`
   - `road.py`
   - `interactions.py`
   - `ratioAI.pkl`
   - `data.pkl`

3. Run the simulation:

   ```bash
   python app_2.py
   ```

4. Enter a dataset row number when prompted:

   ```text
   Input row num: 0
   ```

5. Use the keyboard controls to interact with the simulation.

---

## Displayed Statistics

The simulation displays:

- Number of cars
- Number of people
- Car:People ratio
- Same light time
- Extreme weather status
- Temperature
- Current hour
- Day of week
- Holiday indicator
- Predicted traffic volume
- People vs Car priority bars

---

## Example Scenario Setup

In `app_2.py`, the road and traffic light are created like this:

```python
roads = [
    Road(300, [
        TrafficLight(TRAFFIC_LIGHT_Y),
    ], [], data_num_waiting_car, data_num_waiting_people)
]
```

The road is vertical, the traffic light is placed at `TRAFFIC_LIGHT_Y`, and the dataset row controls the number of waiting cars and people.

---

## Summary

This is an **AI-controlled traffic light simulation** where:

- Pygame handles rendering and interaction.
- XGBoost predicts whether people or cars should go first.
- Cars and pedestrians move with acceleration, deceleration, and collision avoidance.
- The traffic light switches every 15 seconds if the intersection is clear.
- Scenarios are loaded from `data.pkl` and selected by row number.

Use `app_2.py` as the main entry point.
