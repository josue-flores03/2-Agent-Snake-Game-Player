import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
from pygame import math
import math
pygame.init()
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 40

class SnakeGameAI:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        self.prev_distance1 = self.cal_distance1()

    def reset(self):
        #init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def cal_distance1(self):
        x1,y1 = self.head
        x2,y2 = self.food

        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)

        return distance



    def update_distance1(self):
        #maybe add a if staments that makes the reward null or opposite if their is a collision in the way maybe distance between collision + collision to newdistance == new distance
        new_distance1=self.cal_distance1()
        if new_distance1 < self.prev_distance1:
            self.prev_distance1=new_distance1
            x=5
        elif new_distance1 == self.prev_distance1:
            x=0
        elif new_distance1 > self.prev_distance1:

            self.prev_distance1 = new_distance1
            x=-10
        return x


        return x
    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        reward += self.update_distance1()
        if self.is_collision() or self.frame_iteration > 50  * len(self.snake):
            game_over = True
            reward = -100
            return reward, game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward += 50
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt = None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: #[0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)



# import pygame
# import random
# from enum import Enum
# from collections import namedtuple
# import numpy as np

# pygame.init()
# font = pygame.font.SysFont('arial', 25)

# class Direction(Enum):
#     RIGHT = 1
#     LEFT = 2
#     UP = 3
#     DOWN = 4
    
# Point = namedtuple('Point', 'x, y')

# # Possible circles in a 2 x 2 area
# two_by_two_uldr = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
# two_by_two_urdl = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
# two_by_two_dlur = [Direction.DOWN, Direction.LEFT, Direction.UP, Direction.RIGHT]
# two_by_two_drul = [Direction.DOWN, Direction.RIGHT, Direction.UP, Direction.LEFT]
# two_by_two_lurd = [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN]
# two_by_two_ldru = [Direction.LEFT, Direction.DOWN, Direction.RIGHT, Direction.UP]
# two_by_two_ruld = [Direction.RIGHT, Direction.UP, Direction.LEFT, Direction.DOWN]
# two_by_two_rdlu = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]


# # rgb colors
# WHITE = (255, 255, 255)
# RED = (200,0,0)
# BLUE = (0, 0, 255)
# BLACK = (0,0,0)

# BLOCK_SIZE = 20
# SPEED = 40

# class SnakeGameAI:
    
#     def __init__(self, w=640, h=480):
#         self.w = w
#         self.h = h
#         self.directions = []
#         # init display
#         self.display = pygame.display.set_mode((self.w, self.h))
#         pygame.display.set_caption('Snake')
#         self.clock = pygame.time.Clock()
#         self.reset()

#     def reset(self):
#         #init game state
#         self.direction = Direction.RIGHT

#         self.head = Point(self.w/2, self.h/2)
#         self.snake = [self.head, 
#                       Point(self.head.x-BLOCK_SIZE, self.head.y),
#                       Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
#         self.score = 0
#         self.food = None
#         self._place_food()
#         self.frame_iteration = 0
#         self.directions.clear()
        
#     def _place_food(self):
#         x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
#         y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
#         self.food = Point(x, y)
#         if self.food in self.snake:
#             self._place_food()
        
#     def play_step(self, action):
#         self.frame_iteration += 1
#         # 1. collect user input
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 quit()
        
#         # 2. move
#         self._move(action) # update the head
#         self.snake.insert(0, self.head)
        
#         # 3. check if game over
#         reward = 0
#         game_over = False
#         if self.is_collision() or self.frame_iteration > 50  * len(self.snake):
#             game_over = True
#             reward = -10
#             return reward, game_over, self.score
            
#         # 4. place new food or just move
#         if self.head == self.food:
#             self.score += 1
#             reward = 10
#             self._place_food()
#         else:
#             self.snake.pop()

#         # 5. check if the snake is going in a circle
#         # if self._check_circle():
#         #     reward -= 5
#         #     print('AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH')
        
#         # 6. update ui and clock
#         self._update_ui()
#         self.clock.tick(SPEED)

#         # 7 update list of directions
#         self.directions.append(self.direction)

#         # 8. return game over and score
#         return reward, game_over, self.score
    
#     def is_collision(self, pt = None):
#         if pt is None:
#             pt = self.head
#         # hits boundary
#         if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
#             return True
#         # hits itself
#         if pt in self.snake[1:]:
#             return True
        
#         return False
        
#     def _update_ui(self):
#         self.display.fill(BLACK)
        
#         for pt in self.snake:
#             pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
#         pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
#         text = font.render("Score: " + str(self.score), True, WHITE)
#         self.display.blit(text, [0, 0])
#         pygame.display.flip()
        
#     def _move(self, action):
#         # [straight, right, left]

#         clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
#         idx = clock_wise.index(self.direction)

#         if np.array_equal(action, [1, 0, 0]):
#             new_dir = clock_wise[idx] # no change
#         elif np.array_equal(action, [0, 1, 0]):
#             next_idx = (idx + 1) % 4
#             new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
#         else: #[0, 0, 1]
#             next_idx = (idx - 1) % 4
#             new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

#         self.direction = new_dir

#         x = self.head.x
#         y = self.head.y
#         if self.direction == Direction.RIGHT:
#             x += BLOCK_SIZE
#         elif self.direction == Direction.LEFT:
#             x -= BLOCK_SIZE
#         elif self.direction == Direction.DOWN:
#             y += BLOCK_SIZE
#         elif self.direction == Direction.UP:
#             y -= BLOCK_SIZE
            
#         self.head = Point(x, y)

#     def _check_circle(self):
#         if len(self.directions) >= 4:
#             previous_directions = [self.directions[-4], self.directions[-3], self.directions[-2], self.directions[-1]]
#             if previous_directions == two_by_two_uldr:
#                 return True
#             if previous_directions == two_by_two_urdl: 
#                 return True
#             if previous_directions == two_by_two_dlur:
#                 return True
#             if previous_directions == two_by_two_drul:
#                 return True
#             if previous_directions == two_by_two_lurd:
#                 return True
#             if previous_directions == two_by_two_ldru:
#                 return True
#             if previous_directions == two_by_two_ruld:
#                 return True
#             if previous_directions == two_by_two_rdlu:
#                 return True
#         return False
