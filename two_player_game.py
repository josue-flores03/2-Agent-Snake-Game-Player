import pygame
import random
from enum import Enum
from collections import namedtuple

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
SPEED = 25

class SnakeGame:
    
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
                      Point((self.w / 2) + (2 * BLOCK_SIZE), (self.h / 2) + (2 * BLOCK_SIZE))]
        
        self.head2 = Point(self.w / 2, (self.h / 2 ) - (2 * BLOCK_SIZE))
        self.snake2 =  [self.head2, 
                        Point((self.w / 2) - (2 * BLOCK_SIZE), (self.h / 2 ) - (2 * BLOCK_SIZE))]
        
        self.score = 0
        self.food1 = None
        self.food2 = None
        self._place_food()
        self._place_food()
    
    
    
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
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not self.direction1 == Direction.RIGHT:
                    self.direction1 = Direction.LEFT
                elif event.key == pygame.K_RIGHT and not self.direction1 == Direction.LEFT:
                    self.direction1 = Direction.RIGHT
                elif event.key == pygame.K_UP and not self.direction1 == Direction.DOWN:
                    self.direction1 = Direction.UP
                elif event.key == pygame.K_DOWN and not self.direction1 == Direction.UP:
                    self.direction1 = Direction.DOWN
                
                if event.key == pygame.K_a and not self.direction2 == Direction.RIGHT:
                    self.direction2 = Direction.LEFT
                elif event.key == pygame.K_d and not self.direction2 == Direction.LEFT:
                    self.direction2 = Direction.RIGHT
                elif event.key == pygame.K_w and not self.direction2 == Direction.DOWN:
                    self.direction2 = Direction.UP
                elif event.key == pygame.K_s and not self.direction2 == Direction.UP:
                    self.direction2 = Direction.DOWN
        
        # 2. move if alive
        if self.alive1:
            self.head1 = self._move(self.direction1, self.head1) # update the head of first snake
            self.snake1.insert(0, self.head1)
        
        if self.alive2:
            self.head2 = self._move(self.direction2, self.head2) # update the head of the second snake
            self.snake2.insert(0, self.head2)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move if alive
        if self.alive1:
            if self.head1 == self.food1 or self.head1 == self.food2:
                self.score += 1
                self._place_food()
            else:
                self.snake1.pop()

        if self.alive2:
            if self.head2 == self.food1 or self.head2 == self.food2:
                self.score += 1
                self._place_food()
            else:
                self.snake2.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
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
        
    def _move(self, direction, head):
        x = head.x
        y = head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        head = Point(x, y)
        return head
            

if __name__ == '__main__':
    game = SnakeGame()
    max_score = 0
    # game loop
    while True:
        game_over, score = game.play_step()

        if game_over == True:
            if score > max_score:
                max_score = score
            print('Score: ', score, "\tMax Score: ", max_score)
            game.reset()
        
        
    # pygame.quit()


# import pygame
# import random
# from enum import Enum
# from collections import namedtuple

# pygame.init()
# font = pygame.font.SysFont('arial', 25)

# class Direction(Enum):
#     RIGHT = 1
#     LEFT = 2
#     UP = 3
#     DOWN = 4
    
# Point = namedtuple('Point', 'x, y')

# # rgb colors
# WHITE = (255, 255, 255)
# RED = (200,0,0)
# BLUE = (0, 0, 255)
# GREEN = (0, 255, 0)
# BLACK = (0,0,0)

# BLOCK_SIZE = 20
# SPEED = 10

# class SnakeGame:
    
#     def __init__(self, w=640, h=480):
#         self.w = w
#         self.h = h
#         # init display
#         self.display = pygame.display.set_mode((self.w, self.h))
#         pygame.display.set_caption('Snake')
#         self.clock = pygame.time.Clock()
        
#         # init game state
#         self.direction1 = Direction.RIGHT
#         self.direction2 = Direction.RIGHT

#         self.alive1 = True
#         self.alive2 = True
        
#         self.head1 = Point(self.w / 2, self.h / 2)
#         self.snake1 = [self.head1, 
#                       Point(self.head1.x - BLOCK_SIZE, self.head1.y),
#                       Point(self.head1.x - (2 * BLOCK_SIZE), self.head1.y)]
        
#         self.head2 = Point(self.w / 2, (self.h / 2 ) - (2 * BLOCK_SIZE))
#         self.snake2 =  [self.head2, 
#                         Point(self.head2.x - BLOCK_SIZE, self.head2.y),
#                         Point(self.head2.x - (2 * BLOCK_SIZE), self.head2.y)]
        
#         self.score = 0
#         self.food1 = None
#         self.food2 = None
#         self._place_food()
#         self._place_food()
        
#     def _place_food(self):
#         if self.food1 == None:
#             x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
#             y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
#             self.food1 = Point(x, y)
        
#         if self.food2 == None:
#             x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
#             y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
#             self.food2 = Point(x, y)

#         if self.food1 in self.snake1 or self.food1 in self.snake2:
#             self.food1 = None
#             self._place_food()

#         if self.food2 in self.snake1 or self.food2 in self.snake2:
#             self.food2 = None
#             self._place_food()
        
#     def play_step(self):
#         # 1. collect user input
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 quit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LEFT and not self.direction1 == Direction.RIGHT:
#                     self.direction1 = Direction.LEFT
#                 elif event.key == pygame.K_RIGHT and not self.direction1 == Direction.LEFT:
#                     self.direction1 = Direction.RIGHT
#                 elif event.key == pygame.K_UP and not self.direction1 == Direction.DOWN:
#                     self.direction1 = Direction.UP
#                 elif event.key == pygame.K_DOWN and not self.direction1 == Direction.UP:
#                     self.direction1 = Direction.DOWN
                
#                 if event.key == pygame.K_a and not self.direction2 == Direction.RIGHT:
#                     self.direction2 = Direction.LEFT
#                 elif event.key == pygame.K_d and not self.direction2 == Direction.LEFT:
#                     self.direction2 = Direction.RIGHT
#                 elif event.key == pygame.K_w and not self.direction2 == Direction.DOWN:
#                     self.direction2 = Direction.UP
#                 elif event.key == pygame.K_s and not self.direction2 == Direction.UP:
#                     self.direction2 = Direction.DOWN
        
#         # 2. move if alive
#         if self.alive1:
#             self.head1 = self._move(self.direction1, self.head1) # update the head of first snake
#             self.snake1.insert(0, self.head1)
        
#         if self.alive2:
#             self.head2 = self._move(self.direction2, self.head2) # update the head of the second snake
#             self.snake2.insert(0, self.head2)
        
#         # 3. check if game over
#         game_over = False
#         if self._is_collision():
#             game_over = True
#             return game_over, self.score
            
#         # 4. place new food or just move if alive
#         if self.alive1:
#             if self.head1 == self.food1 or self.head1 == self.food2:
#                 self.score += 1
#                 self._place_food()
#             else:
#                 self.snake1.pop()

#         if self.alive2:
#             if self.head2 == self.food1 or self.head2 == self.food2:
#                 self.score += 1
#                 self._place_food()
#             else:
#                 self.snake2.pop()
        
#         # 5. update ui and clock
#         self._update_ui()
#         self.clock.tick(SPEED)
#         # 6. return game over and score
#         return game_over, self.score
    
#     def _is_collision(self):
#         # hits boundary
#         if self.head1.x > self.w - BLOCK_SIZE or self.head1.x < 0 or self.head1.y > self.h - BLOCK_SIZE or self.head1.y < 0:
#             self.alive1 = False
#         if self.head2.x > self.w - BLOCK_SIZE or self.head2.x < 0 or self.head2.y > self.h - BLOCK_SIZE or self.head2.y < 0:
#             self.alive2 = False

#         # hits itself
#         if self.head1 in self.snake1[1:]:
#             self.alive1 = False
#         if self.head2 in self.snake2[1:]:
#             self.alive2 = False

#         # hits other snake
#         if self.head1 in self.snake2[1:]:
#             self.alive1 = False
#         if self.head2 in self.snake1[1:]:
#             self.alive2 = False  

#         if not self.alive1 and not self.alive2:
#             return True
#         return False
        
#     def _update_ui(self):
#         self.display.fill(BLACK)
        
#         for pt in self.snake1:
#             pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

#         for pt in self.snake2:
#             pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
#         pygame.draw.rect(self.display, RED, pygame.Rect(self.food1.x, self.food1.y, BLOCK_SIZE, BLOCK_SIZE))
#         pygame.draw.rect(self.display, RED, pygame.Rect(self.food2.x, self.food2.y, BLOCK_SIZE, BLOCK_SIZE))
        
#         text = font.render("Score: " + str(self.score), True, WHITE)
#         self.display.blit(text, [0, 0])
#         pygame.display.flip()
        
#     def _move(self, direction, head):
#         x = head.x
#         y = head.y
#         if direction == Direction.RIGHT:
#             x += BLOCK_SIZE
#         elif direction == Direction.LEFT:
#             x -= BLOCK_SIZE
#         elif direction == Direction.DOWN:
#             y += BLOCK_SIZE
#         elif direction == Direction.UP:
#             y -= BLOCK_SIZE

#         head = Point(x, y)
#         return head
            

# if __name__ == '__main__':
#     game = SnakeGame()
    
#     # game loop
#     while True:
#         game_over, score = game.play_step()

#         if game_over == True:
#             break
        
#     print('Final Score', score)
        
        
#     pygame.quit()
