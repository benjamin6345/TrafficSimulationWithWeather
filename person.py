import pygame
from constants import *
class Person:
    speed: int
    color: int
    max_speed: int
    prev_updated_time: float
    decelerating: bool
    accelerating: bool
    position: tuple[int, int]


    manual_decelerate: bool = False

    def __init__(self, side:str):
        self.color = (0, 0, 255) # 车子颜色
        self.position = None
        self.side = side
        
    # 根据速度以及上一次self.prev_updated_time，用s=vt公式计算距离，把车子原本的y坐标减去距离就会得到新位置（车子往上走的）
    def move(self) -> None:
        x, y = self.position
        if self.side == 'left':
            x += 1
            
        else:
            x -= 1
            
        self.position = (x, y)

    # 把车子显示在屏幕里
    def draw(self, window: pygame.Surface) -> None:
        x, y = self.position
        x = int(x)
        y = int(y)
        pygame.draw.circle(window, self.color, (x, y), PERSON_CIRCLE_RADIUS)


