import torch
import random
import numpy as np
from collections import deque # to store memory
from one_player_npg import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from graph_plots import plot
import tkinter as tk
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
lr = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # control randomness
        self.gamma = 0.9 # discount rate (MUST be smaller than 1)
        self.memory = deque(maxlen = MAX_MEMORY) # popleft() automatically
        self.model = Linear_QNet(18, 256, 64, 3) # input is size of states, output is size of action
        self.trainer = QTrainer(self.model, lr = lr, gamma = self.gamma)


    def get_state(self, game):
        head = game.snake[0]

        # Get the four squares around the snake head
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        point_l_u = Point(head.x - 20, head.y - 20)
        point_l_d = Point(head.x - 20, head.y + 20)
        point_r_u = Point(head.x + 20, head.y - 20)
        point_r_d = Point(head.x + 20, head.y + 20)

        point_l_2 = Point(head.x - 40, head.y)
        point_r_2 = Point(head.x + 40, head.y)
        point_u_2 = Point(head.x, head.y - 40)
        point_d_2 = Point(head.x, head.y + 40)

        point_l_2_u_2 = Point(head.x - 40, head.y - 40)
        point_l_2_d_2 = Point(head.x - 40, head.y + 40)
        point_r_2_u_2 = Point(head.x + 40, head.y - 40)
        point_r_2_d_2 = Point(head.x + 40, head.y + 40)

        point_l_u_2 = Point(head.x - 20, head.y - 40)
        point_l_d_2 = Point(head.x - 20, head.y + 40)
        point_r_u_2 = Point(head.x + 20, head.y - 40)
        point_r_d_2 = Point(head.x + 20, head.y + 40)

        point_l_2_u = Point(head.x - 40, head.y - 20)
        point_l_2_d = Point(head.x - 40, head.y + 20)
        point_r_2_u = Point(head.x + 40, head.y - 20)
        point_r_2_d = Point(head.x + 40, head.y + 20)

        # Get the current snake direction
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)), 

            # Danger right
            (dir_r and game.is_collision(point_d)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)), 

            # Danger left
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)),

            # Danger straight 2 blocks away
            (dir_r and game.is_collision(point_r_2)) or 
            (dir_l and game.is_collision(point_l_2)) or 
            (dir_u and game.is_collision(point_u_2)) or 
            (dir_d and game.is_collision(point_d_2)),

            # Danger right 2 blocks away
            (dir_r and game.is_collision(point_d_2)) or 
            (dir_l and game.is_collision(point_u_2)) or 
            (dir_u and game.is_collision(point_r_2)) or 
            (dir_d and game.is_collision(point_l_2)),

            # Danger left 2 blocks away
            (dir_r and game.is_collision(point_u_2)) or
            (dir_l and game.is_collision(point_d_2)) or
            (dir_u and game.is_collision(point_l_2)) or
            (dir_d and game.is_collision(point_r_2)),

            # Danger ring straight left
            (dir_r and game.is_collision(point_r_u)) or
            (dir_l and game.is_collision(point_l_d)) or
            (dir_u and game.is_collision(point_l_u)) or
            (dir_d and game.is_collision(point_r_d)),

            # Danger ring straight right
            (dir_r and game.is_collision(point_r_d)) or
            (dir_l and game.is_collision(point_l_u)) or
            (dir_u and game.is_collision(point_r_u)) or
            (dir_d and game.is_collision(point_l_d)),

            # Danger ring back left
            (dir_r and game.is_collision(point_l_u)) or
            (dir_l and game.is_collision(point_r_d)) or
            (dir_u and game.is_collision(point_l_d)) or
            (dir_d and game.is_collision(point_r_u)),

            # Danger ring back right
            (dir_r and game.is_collision(point_l_d)) or
            (dir_l and game.is_collision(point_r_u)) or
            (dir_u and game.is_collision(point_r_d)) or
            (dir_d and game.is_collision(point_l_u)),  

            # Move direction (only one should be true)
            dir_l, 
            dir_r, 
            dir_u, 
            dir_d,

            # Food location
            game.food.x < game.head.x, # Food is left
            game.food.x > game.head.x, # Food is right
            game.food.y < game.head.y, # Food is up
            game.food.y > game.head.y # Food is down
        ]

        return np.array(state, dtype = int)


    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) # Popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
        else:
            memory_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*memory_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over) # Train for a single step

    def get_action(self, state):
        # random moves: (tradeoff between exploration and exploitation)
        self.epsilon = 80 - self.n_games # play around with hard coded 80
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2) 
            final_move[move] = 1
        else:
            state_0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state_0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move
    

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    reward_total=0
    while True:
        # get old state
        old_state = agent.get_state(game)

        # get move (or action)
        final_move = agent.get_action(old_state)

        # perform move and get new state
        reward, game_over, score = game.play_step(final_move)
        reward_total+=reward
        new_state = agent.get_state(game)
        # train short memory (one step)
        agent.train_short_memory(old_state, final_move, reward, new_state, game_over)

        # remember
        agent.remember(old_state, final_move, reward, new_state, game_over)

        if game_over:
            # train long memory (or replay memory) and plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save() 
            
            print('Game ', agent.n_games, 'Score ', score, "Record ", record,"Reward",reward_total)
            reward_total=0
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    snake = SnakeGameAI()
    train()



# import torch
# import random
# import numpy as np
# from collections import deque # to store memory
# from one_player_npg import SnakeGameAI, Direction, Point
# from model import Linear_QNet, QTrainer
# from graph_plots import plot

# MAX_MEMORY = 100_000
# BATCH_SIZE = 1000
# lr = 0.001

# class Agent:

#     def __init__(self):
#         self.n_games = 0
#         self.epsilon = 0 # control randomness
#         self.gamma = 0.9 # discount rate (MUST be smaller than 1)
#         self.memory = deque(maxlen = MAX_MEMORY) # popleft() automatically
#         self.model = Linear_QNet(11, 256, 3) # input is size of states, output is size of action
#         self.trainer = QTrainer(self.model, lr = lr, gamma = self.gamma)


#     def get_state(self, game):
#         head = game.snake[0]

#         # Get the four squares around the snake head
#         point_l = Point(head.x - 20, head.y)
#         point_r = Point(head.x + 20, head.y)
#         point_u = Point(head.x, head.y - 20)
#         point_d = Point(head.x, head.y + 20)

#         # Get the current snake direction
#         dir_l = game.direction == Direction.LEFT
#         dir_r = game.direction == Direction.RIGHT
#         dir_u = game.direction == Direction.UP
#         dir_d = game.direction == Direction.DOWN

#         state = [
#             # Danger straight
#             (dir_r and game.is_collision(point_r)) or 
#             (dir_l and game.is_collision(point_l)) or 
#             (dir_u and game.is_collision(point_u)) or 
#             (dir_d and game.is_collision(point_d)), 

#             # Danger right
#             (dir_r and game.is_collision(point_d)) or 
#             (dir_l and game.is_collision(point_u)) or 
#             (dir_u and game.is_collision(point_r)) or 
#             (dir_d and game.is_collision(point_l)), 

#             # Danger left
#             (dir_r and game.is_collision(point_u)) or
#             (dir_l and game.is_collision(point_d)) or
#             (dir_u and game.is_collision(point_l)) or
#             (dir_d and game.is_collision(point_r)),

#             # Move direction (only one should be true)
#             dir_l, 
#             dir_r, 
#             dir_u, 
#             dir_d,

#             # Food location
#             game.food.x < game.head.x, # Food is left
#             game.food.x > game.head.x, # Food is right
#             game.food.y < game.head.y, # Food is up
#             game.food.y > game.head.y # Food is down
#         ]

#         return np.array(state, dtype = int)


#     def remember(self, state, action, reward, next_state, game_over):
#         self.memory.append((state, action, reward, next_state, game_over)) # Popleft if MAX_MEMORY is reached

#     def train_long_memory(self):
#         if len(self.memory) > BATCH_SIZE:
#             memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
#         else:
#             memory_sample = self.memory

#         states, actions, rewards, next_states, game_overs = zip(*memory_sample)
#         self.trainer.train_step(states, actions, rewards, next_states, game_overs)

#     def train_short_memory(self, state, action, reward, next_state, game_over):
#         self.trainer.train_step(state, action, reward, next_state, game_over) # Train for a single step

#     def get_action(self, state):
#         # random moves: (tradeoff between exploration and exploitation)
#         self.epsilon = 80 - self.n_games # play around with hard coded 80
#         final_move = [0, 0, 0]
#         if random.randint(0, 200) < self.epsilon:
#             move = random.randint(0, 2) 
#             final_move[move] = 1
#         else:
#             state_0 = torch.tensor(state, dtype = torch.float)
#             prediction = self.model(state_0)
#             move = torch.argmax(prediction).item()
#             final_move[move] = 1
        
#         return final_move
    

# def train():
#     plot_scores = []
#     plot_mean_scores = []
#     total_score = 0
#     record = 0
#     agent = Agent()
#     game = SnakeGameAI()

#     while True:
#         # get old state
#         old_state = agent.get_state(game)

#         # get move (or action)
#         final_move = agent.get_action(old_state)

#         # perform move and get new state
#         reward, game_over, score = game.play_step(final_move)
#         new_state = agent.get_state(game)
#         # train short memory (one step)
#         agent.train_short_memory(old_state, final_move, reward, new_state, game_over)

#         # remember
#         agent.remember(old_state, final_move, reward, new_state, game_over)

#         if game_over:
#             # train long memory (or replay memory) and plot result
#             game.reset()
#             agent.n_games += 1
#             agent.train_long_memory()

#             if score > record:
#                 record = score
#                 agent.model.save() 
            
#             print('Game ', agent.n_games, 'Score ', score, "Record ", record)

#             plot_scores.append(score)
#             total_score += score
#             mean_score = total_score / agent.n_games
#             plot_mean_scores.append(mean_score)
#             plot(plot_scores, plot_mean_scores)


# if __name__ == '__main__':
#     train()
