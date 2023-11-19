import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

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
GREEN = (0, 255, 0)
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
    


    def reset(self):
        # init game state
        self.direction1 = Direction.RIGHT
        self.direction2 = Direction.RIGHT

        self.alive1 = True
        self.alive2 = True
        
        self.head1 = Point(self.w / 2, self.h / 2)
        self.snake1 = [self.head1, 
                      Point(self.head1.x - BLOCK_SIZE, self.head1.y),
                      Point(self.head1.x - (2 * BLOCK_SIZE), self.head1.y)]
        
        self.head2 = Point(self.w / 2, (self.h / 2 ) - (2 * BLOCK_SIZE))
        self.snake2 =  [self.head2, 
                        Point(self.head2.x - BLOCK_SIZE, self.head2.y),
                        Point(self.head2.x - (2 * BLOCK_SIZE), self.head2.y)]
        
        self.score = 0
        self.food1 = None
        self.food2 = None
        self._place_food()
        self._place_food()
        self.frame_iteration = 0
        


    def _place_food(self):
        if self.food1 == None:
            x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
            y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
            self.food1 = Point(x, y)
        
        if self.food2 == None:
            x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
            y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
            self.food2 = Point(x, y)

        if self.food1 in self.snake1 or self.food1 in self.snake2:
            self.food1 = None
            self._place_food()

        if self.food2 in self.snake1 or self.food2 in self.snake2:
            self.food2 = None
            self._place_food()
        


    def play_step(self, action_1, action_2):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move if alive
        if self.alive1:
            self._move(action_1, '1') # update the head of first snake
            self.snake1.insert(0, self.head1)
        
        if self.alive2:
            self._move(action_2, '2') # update the head of the second snake
            self.snake2.insert(0, self.head2)

        # 3. check if collisions or game over
        reward = 0
        game_over = False
        # Both snakes are dead
        if self.is_collision() or self.frame_iteration > 25 * len(self.snake1) or self.frame_iteration > 25 * len(self.snake2):
            game_over = True
            reward = -10
            return reward, game_over, self.score
        
        # # One snake is dead
        # if not self.is_collision():
        #     if self.alive1 and not self.alive2 or not self.alive1 and self.alive2:
        #         reward += -10
            
        # 4. place new food or just move if alive
        if self.alive1:
            if self.head1 == self.food1 or self.head1 == self.food2:
                self.score += 1
                reward += 10
                self._place_food()
            else:
                self.snake1.pop()

        if self.alive2:
            if self.head2 == self.food1 or self.head2 == self.food2:
                self.score += 1
                reward += 10
                self._place_food()
            else:
                self.snake2.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score
    


    def is_collision(self, pt = None):
        #print(self.head1.x)
        if pt is not None:
            # hits boundary
            if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
                return True
            # hits itself
            if pt in self.snake1[1:] or pt in self.snake2[1:]:
                return True
            return False
        
        else:
            # hits boundary
            if self.head1.x > self.w - BLOCK_SIZE or self.head1.x < 0 or self.head1.y > self.h - BLOCK_SIZE or self.head1.y < 0:
                self.alive1 = False
            if self.head2.x > self.w - BLOCK_SIZE or self.head2.x < 0 or self.head2.y > self.h - BLOCK_SIZE or self.head2.y < 0:
                self.alive2 = False

            # hits itself
            if self.head1 in self.snake1[1:]:
                self.alive1 = False
            if self.head2 in self.snake2[1:]:
                self.alive2 = False

            # hits other snake
            if self.head1 in self.snake2[1:]:
                self.alive1 = False
            if self.head2 in self.snake1[1:]:
                self.alive2 = False  

            if not self.alive1 or not self.alive2:
                return True
            return False
        


    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake1:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        for pt in self.snake2:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food1.x, self.food1.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food2.x, self.food2.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        


    def _move(self, action, head):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        if head == '1':
            idx = clock_wise.index(self.direction1)
        elif head == '2':
            idx = clock_wise.index(self.direction2)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: #[0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        if head == '1':
            self.direction1 = new_dir
        elif head == '2':
            self.direction2 = new_dir


        if head == '1':
            x = self.head1.x
            y = self.head1.y

            if self.direction1 == Direction.RIGHT:
                x += BLOCK_SIZE
            elif self.direction1 == Direction.LEFT:
                x -= BLOCK_SIZE
            elif self.direction1 == Direction.DOWN:
                y += BLOCK_SIZE
            elif self.direction1 == Direction.UP:
                y -= BLOCK_SIZE

            self.head1 = Point(x, y)
        elif head == '2':
            x = self.head2.x
            y = self.head2.y

            if self.direction2 == Direction.RIGHT:
                x += BLOCK_SIZE
            elif self.direction2 == Direction.LEFT:
                x -= BLOCK_SIZE
            elif self.direction2 == Direction.DOWN:
                y += BLOCK_SIZE
            elif self.direction2 == Direction.UP:
                y -= BLOCK_SIZE

            self.head2 = Point(x, y)
    