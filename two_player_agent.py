import torch
import random
import numpy as np
from collections import deque # to store memory
from two_player_npg import SnakeGameAI, Direction, Point
from two_player_model import Linear_QNet, QTrainer, Combination
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
        # self.model = Linear_QNet(30, 256, 3) # input is size of states, output is size of action
        self.model = Linear_QNet(23, 256, 64, 3) # input is size of states, output is size of action
        self.trainer = QTrainer(self.model, lr = lr, gamma = self.gamma)



    def get_state(self, game, snake1):
        head1 = game.snake1[0]
        head2 = game.snake2[0]

        # Get the four squares around the snake 1 head
        point_l1 = Point(head1.x - 20, head1.y)
        point_r1 = Point(head1.x + 20, head1.y)
        point_u1 = Point(head1.x, head1.y - 20)
        point_d1 = Point(head1.x, head1.y + 20)

        # Get the current snake 1 direction 
        dir_l1 = game.direction1 == Direction.LEFT
        dir_r1 = game.direction1 == Direction.RIGHT
        dir_u1 = game.direction1 == Direction.UP
        dir_d1 = game.direction1 == Direction.DOWN

        # Get the four squares around the snake 2 head
        point_l2 = Point(head2.x - 20, head2.y)
        point_r2 = Point(head2.x + 20, head2.y)
        point_u2 = Point(head2.x, head2.y - 20)
        point_d2 = Point(head2.x, head2.y + 20)

        # Get the current snake 2 direction 
        dir_l2 = game.direction2 == Direction.LEFT
        dir_r2 = game.direction2 == Direction.RIGHT
        dir_u2 = game.direction2 == Direction.UP
        dir_d2 = game.direction2 == Direction.DOWN

        point_l_u1 = Point(head1.x - 20, head1.y - 20)
        point_l_d1 = Point(head1.x - 20, head1.y + 20)
        point_r_u1 = Point(head1.x + 20, head1.y - 20)
        point_r_d1 = Point(head1.x + 20, head1.y + 20)

        point_l_21 = Point(head1.x - 40, head1.y)
        point_r_21 = Point(head1.x + 40, head1.y)
        point_u_21 = Point(head1.x, head1.y - 40)
        point_d_21 = Point(head1.x, head1.y + 40)

        point_l_u2 = Point(head2.x - 20, head2.y - 20)
        point_l_d2 = Point(head2.x - 20, head2.y + 20)
        point_r_u2 = Point(head2.x + 20, head2.y - 20)
        point_r_d2 = Point(head2.x + 20, head2.y + 20)

        point_l_22 = Point(head2.x - 40, head2.y)
        point_r_22 = Point(head2.x + 40, head2.y)
        point_u_22 = Point(head2.x, head2.y - 40)
        point_d_22 = Point(head2.x, head2.y + 40)

        if snake1:
            state = [
                # Danger straight snake 1
                (dir_r1 and game.is_collision(point_r1)) or 
                (dir_l1 and game.is_collision(point_l1)) or 
                (dir_u1 and game.is_collision(point_u1)) or 
                (dir_d1 and game.is_collision(point_d1)), 

                # Danger right snake 1
                (dir_r1 and game.is_collision(point_d1)) or 
                (dir_l1 and game.is_collision(point_u1)) or 
                (dir_u1 and game.is_collision(point_r1)) or 
                (dir_d1 and game.is_collision(point_l1)),

                # Danger left snake 1
                (dir_r1 and game.is_collision(point_u1)) or
                (dir_l1 and game.is_collision(point_d1)) or
                (dir_u1 and game.is_collision(point_l1)) or
                (dir_d1 and game.is_collision(point_r1)),

                # Danger ring straight left
                (dir_r1 and game.is_collision(point_r_u1)) or
                (dir_l1 and game.is_collision(point_l_d1)) or
                (dir_u1 and game.is_collision(point_l_u1)) or
                (dir_d1 and game.is_collision(point_r_d1)),

                # Danger ring straight right
                (dir_r1 and game.is_collision(point_r_d1)) or
                (dir_l1 and game.is_collision(point_l_u1)) or
                (dir_u1 and game.is_collision(point_r_u1)) or
                (dir_d1 and game.is_collision(point_l_d1)),

                # Danger ring back left
                (dir_r1 and game.is_collision(point_l_u1)) or
                (dir_l1 and game.is_collision(point_r_d1)) or
                (dir_u1 and game.is_collision(point_l_d1)) or
                (dir_d1 and game.is_collision(point_r_u1)),

                # Danger ring back right
                (dir_r1 and game.is_collision(point_l_d1)) or
                (dir_l1 and game.is_collision(point_r_u1)) or
                (dir_u1 and game.is_collision(point_r_d1)) or
                (dir_d1 and game.is_collision(point_l_u1)),  

                # Move direction snake 1 (only one should be true)
                dir_l1, 
                dir_r1, 
                dir_u1, 
                dir_d1,

                # Food 1 location for snake 1
                game.food1.x < game.head1.x, # Food 1 is left of snake 1
                game.food1.x > game.head1.x, # Food 1 is right of snake 1
                game.food1.y < game.head1.y, # Food 1 is up of snake 1
                game.food1.y > game.head1.y, # Food 1 is down of snake 1

                # Food 2 location for snake 1
                game.food2.x < game.head1.x, # Food 2 is left of snake 1
                game.food2.x > game.head1.x, # Food 2 is right of snake 1
                game.food2.y < game.head1.y, # Food 2 is up of snake 1
                game.food2.y > game.head1.y, # Food 2 is down of snake 1

                # snake 2 location for snake 1
                head2.x < head1.x,
                head2.x > head1.x,
                head2.y < head1.y,
                head2.y > head1.y 
            ]

        else:
            state = [
                # Danger straight snake 2
                (dir_r2 and game.is_collision2(point_r2)) or
                (dir_l2 and game.is_collision2(point_l2)) or
                (dir_u2 and game.is_collision2(point_u2)) or
                (dir_d2 and game.is_collision2(point_d2)),

                # Danger right snake 2
                (dir_r2 and game.is_collision2(point_d2)) or
                (dir_l2 and game.is_collision2(point_u2)) or
                (dir_u2 and game.is_collision2(point_r2)) or
                (dir_d2 and game.is_collision2(point_l2)),

                # Danger left snake 2
                (dir_r2 and game.is_collision2(point_u2)) or
                (dir_l2 and game.is_collision2(point_d2)) or
                (dir_u2 and game.is_collision2(point_l2)) or
                (dir_d2 and game.is_collision2(point_r2)),


                # Danger ring straight left
                (dir_r2 and game.is_collision(point_r_u2)) or
                (dir_l2 and game.is_collision(point_l_d2)) or
                (dir_u2 and game.is_collision(point_l_u2)) or
                (dir_d2 and game.is_collision(point_r_d2)),

                # Danger ring straight right
                (dir_r2 and game.is_collision(point_r_d2)) or
                (dir_l2 and game.is_collision(point_l_u2)) or
                (dir_u2 and game.is_collision(point_r_u2)) or
                (dir_d2 and game.is_collision(point_l_d2)),

                # Danger ring back left
                (dir_r2 and game.is_collision(point_l_u2)) or
                (dir_l2 and game.is_collision(point_r_d2)) or
                (dir_u2 and game.is_collision(point_l_d2)) or
                (dir_d2 and game.is_collision(point_r_u2)),

                # Danger ring back right
                (dir_r2 and game.is_collision(point_l_d2)) or
                (dir_l2 and game.is_collision(point_r_u2)) or
                (dir_u2 and game.is_collision(point_r_d2)) or
                (dir_d2 and game.is_collision(point_l_u2)),  

                # Move direction snake 2 (only one should be true)
                dir_l2, 
                dir_r2, 
                dir_u2, 
                dir_d2,

                # Food 1 location for snake 2
                game.food1.x < game.head2.x, # Food 1 is left of snake 2
                game.food1.x > game.head2.x, # Food 1 is right of snake 2
                game.food1.y < game.head2.y, # Food 1 is up of snake 2
                game.food1.y > game.head2.y, # Food 1 is down of snake 2

                # Food 2 location for snake 2
                game.food2.x < game.head2.x, # Food 2 is left of snake 2
                game.food2.x > game.head2.x, # Food 2 is right of snake 2
                game.food2.y < game.head2.y, # Food 2 is up of snake 2
                game.food2.y > game.head2.y, # Food 2 is down of snake 2

                # snake 1 location for snake 2
                head1.x < head2.x,
                head1.x > head2.x,
                head1.y < head2.y,
                head1.y > head2.y 
            ]
        # state = [
        #     # Danger straight snake 1
        #     (dir_r1 and game.is_collision(point_r1)) or 
        #     (dir_l1 and game.is_collision(point_l1)) or 
        #     (dir_u1 and game.is_collision(point_u1)) or 
        #     (dir_d1 and game.is_collision(point_d1)), 

        #     # Danger straight snake 2
        #     (dir_r2 and game.is_collision(point_r2)) or 
        #     (dir_l2 and game.is_collision(point_l2)) or 
        #     (dir_u2 and game.is_collision(point_u2)) or 
        #     (dir_d2 and game.is_collision(point_d2)), 

        #     # Danger right snake 1
        #     (dir_r1 and game.is_collision(point_d1)) or 
        #     (dir_l1 and game.is_collision(point_u1)) or 
        #     (dir_u1 and game.is_collision(point_r1)) or 
        #     (dir_d1 and game.is_collision(point_l1)), 

        #     # Danger right snake 2
        #     (dir_r2 and game.is_collision(point_d2)) or 
        #     (dir_l2 and game.is_collision(point_u2)) or 
        #     (dir_u2 and game.is_collision(point_r2)) or 
        #     (dir_d2 and game.is_collision(point_l2)), 

        #     # Danger left snake 1
        #     (dir_r1 and game.is_collision(point_u1)) or
        #     (dir_l1 and game.is_collision(point_d1)) or
        #     (dir_u1 and game.is_collision(point_l1)) or
        #     (dir_d1 and game.is_collision(point_r1)),

        #     # Danger left snake 2
        #     (dir_r2 and game.is_collision(point_u2)) or
        #     (dir_l2 and game.is_collision(point_d2)) or
        #     (dir_u2 and game.is_collision(point_l2)) or
        #     (dir_d2 and game.is_collision(point_r2)),

        #     # Move direction snake 1(only one should be true)
        #     dir_l1, 
        #     dir_r1, 
        #     dir_u1, 
        #     dir_d1,

        #     # Move direction snake 2
        #     dir_l2, 
        #     dir_r2, 
        #     dir_u2, 
        #     dir_d2,

        #     # Food 1 location for snake 1
        #     game.food1.x < game.head1.x, # Food 1 is left of snake 1
        #     game.food1.x > game.head1.x, # Food 1 is right of snake 1
        #     game.food1.y < game.head1.y, # Food 1 is up of snake 1
        #     game.food1.y > game.head1.y, # Food 1 is down of snake 1

        #     # Food 2 location for snake 1
        #     game.food2.x < game.head1.x, # Food 2 is left of snake 1
        #     game.food2.x > game.head1.x, # Food 2 is right of snake 1
        #     game.food2.y < game.head1.y, # Food 2 is up of snake 1
        #     game.food2.y > game.head1.y, # Food 2 is down of snake 1

        #     # Food 1 location for snake 2
        #     game.food1.x < game.head2.x, # Food 1 is left of snake 2
        #     game.food1.x > game.head2.x, # Food 1 is right of snake 2
        #     game.food1.y < game.head2.y, # Food 1 is up of snake 2
        #     game.food1.y > game.head2.y, # Food 1 is down of snake 2

        #     # Food 2 location for snake 2
        #     game.food2.x < game.head2.x, # Food 2 is left of snake 2
        #     game.food2.x > game.head2.x, # Food 2 is right of snake 2
        #     game.food2.y < game.head2.y, # Food 2 is up of snake 2
        #     game.food2.y > game.head2.y, # Food 2 is down of snake 2
        # ]

        return np.array(state, dtype = int)



    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) # Popleft if MAX_MEMORY is reached



    def train_long_memory(self, model_2, other_model):
        if len(self.memory) > BATCH_SIZE:
            memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
        else:
            memory_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*memory_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs, model_2, other_model)


    def prepare_long_memory_train(self):
        if len(self.memory) > BATCH_SIZE:
            memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
        else:
            memory_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*memory_sample)

        return states, actions, rewards, next_states, game_overs
    

    def train_long_memory_v2(self, total_states, total_actions, total_rewards, total_next_states, total_game_overs):
        self.trainer.train_step(total_states, total_actions, total_rewards, total_next_states, total_game_overs)


    def train_short_memory(self, state, action, reward, next_state, game_over, model_2, other_model):
        self.trainer.train_step(state, action, reward, next_state, game_over, model_2, other_model) # Train for a single step



    def get_action(self, state):
        self.epsilon = 80 - self.n_games 
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
    agent1 = Agent()
    agent2 = Agent()
    game = SnakeGameAI()
    # gamma = 0.9
    reward_total1=0
    reward_total2=0
    # model = Linear_QNet(22, 256, 64, 3) # input is size of states, output is size of action

    while True:
        # get old state
        old_state1 = agent1.get_state(game, True)
        old_state2 = agent2.get_state(game, False)

        # get move (or action)
        final_move1 = agent1.get_action(old_state1)
        final_move2 = agent2.get_action(old_state2)

        # perform move and get new state
        reward1,reward2, game_over, score = game.play_step(final_move1, final_move2)
        reward_total1+=reward1
        reward_total2+=reward2
        new_state1 = agent1.get_state(game, True)
        new_state2 = agent2.get_state(game, False)
        # train short memory (one step)
        agent1.train_short_memory(old_state1, final_move1, reward1, new_state1, game_over, agent2.model, '2')
        agent2.train_short_memory(old_state2, final_move2, reward2, new_state2, game_over, agent1.model, '1')

        # remember
        agent1.remember(old_state1, final_move1, reward1, new_state1, game_over)
        agent2.remember(old_state2, final_move2, reward2, new_state2, game_over)

        if game_over:
            # train long memory (or replay memory) and plot result
            game.reset()
            agent1.n_games += 1
            agent2.n_games = agent1.n_games
            agent1.train_long_memory(agent2.model, '2')
            agent2.train_long_memory(agent1.model, '1')

            if score > record:
                record = score
                agent1.model.save('model1.pth') 
                agent2.model.save('model2.pth')
            print('Game ', agent1.n_games, 'Score ', score, "Record ", record,"Reward_1",reward_total1,"Reward_2",reward_total2)
            reward_total1=0
            reward_total2=0
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent1.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    snake = SnakeGameAI()
    train()




# import torch
# import random
# import numpy as np
# from collections import deque # to store memory
# from two_player_npg import SnakeGameAI, Direction, Point
# from two_player_model import Linear_QNet, QTrainer, Combination
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
#         # self.model = Linear_QNet(30, 256, 3) # input is size of states, output is size of action
#         self.model = Linear_QNet(15, 256, 3) # input is size of states, output is size of action
#         self.trainer = QTrainer(self.model, lr = lr, gamma = self.gamma)



#     def get_state(self, game, snake1):
#         head1 = game.snake1[0]
#         head2 = game.snake2[0]

#         # Get the four squares around the snake 1 head
#         point_l1 = Point(head1.x - 20, head1.y)
#         point_r1 = Point(head1.x + 20, head1.y)
#         point_u1 = Point(head1.x, head1.y - 20)
#         point_d1 = Point(head1.x, head1.y + 20)

#         # Get the current snake 1 direction 
#         dir_l1 = game.direction1 == Direction.LEFT
#         dir_r1 = game.direction1 == Direction.RIGHT
#         dir_u1 = game.direction1 == Direction.UP
#         dir_d1 = game.direction1 == Direction.DOWN

#         # Get the four squares around the snake 2 head
#         point_l2 = Point(head2.x - 20, head2.y)
#         point_r2 = Point(head2.x + 20, head2.y)
#         point_u2 = Point(head2.x, head2.y - 20)
#         point_d2 = Point(head2.x, head2.y + 20)

#         # Get the current snake 2 direction 
#         dir_l2 = game.direction2 == Direction.LEFT
#         dir_r2 = game.direction2 == Direction.RIGHT
#         dir_u2 = game.direction2 == Direction.UP
#         dir_d2 = game.direction2 == Direction.DOWN

#         if snake1:
#             state = [
#                 # Danger straight snake 1
#                 (dir_r1 and game.is_collision(point_r1)) or 
#                 (dir_l1 and game.is_collision(point_l1)) or 
#                 (dir_u1 and game.is_collision(point_u1)) or 
#                 (dir_d1 and game.is_collision(point_d1)), 

#                 # Danger right snake 1
#                 (dir_r1 and game.is_collision(point_d1)) or 
#                 (dir_l1 and game.is_collision(point_u1)) or 
#                 (dir_u1 and game.is_collision(point_r1)) or 
#                 (dir_d1 and game.is_collision(point_l1)),

#                 # Danger left snake 1
#                 (dir_r1 and game.is_collision(point_u1)) or
#                 (dir_l1 and game.is_collision(point_d1)) or
#                 (dir_u1 and game.is_collision(point_l1)) or
#                 (dir_d1 and game.is_collision(point_r1)),

#                 # Move direction snake 1 (only one should be true)
#                 dir_l1, 
#                 dir_r1, 
#                 dir_u1, 
#                 dir_d1,

#                 # Food 1 location for snake 1
#                 game.food1.x < game.head1.x, # Food 1 is left of snake 1
#                 game.food1.x > game.head1.x, # Food 1 is right of snake 1
#                 game.food1.y < game.head1.y, # Food 1 is up of snake 1
#                 game.food1.y > game.head1.y, # Food 1 is down of snake 1

#                 # Food 2 location for snake 1
#                 game.food2.x < game.head1.x, # Food 2 is left of snake 1
#                 game.food2.x > game.head1.x, # Food 2 is right of snake 1
#                 game.food2.y < game.head1.y, # Food 2 is up of snake 1
#                 game.food2.y > game.head1.y, # Food 2 is down of snake 1
#             ]

#         else:
#             state = [
#                 # Danger straight snake 2
#                 (dir_r2 and game.is_collision(point_r2)) or 
#                 (dir_l2 and game.is_collision(point_l2)) or 
#                 (dir_u2 and game.is_collision(point_u2)) or 
#                 (dir_d2 and game.is_collision(point_d2)), 

#                 # Danger right snake 2
#                 (dir_r2 and game.is_collision(point_d2)) or 
#                 (dir_l2 and game.is_collision(point_u2)) or 
#                 (dir_u2 and game.is_collision(point_r2)) or 
#                 (dir_d2 and game.is_collision(point_l2)), 

#                 # Danger left snake 2
#                 (dir_r2 and game.is_collision(point_u2)) or
#                 (dir_l2 and game.is_collision(point_d2)) or
#                 (dir_u2 and game.is_collision(point_l2)) or
#                 (dir_d2 and game.is_collision(point_r2)),

#                 # Move direction snake 2 (only one should be true)
#                 dir_l2, 
#                 dir_r2, 
#                 dir_u2, 
#                 dir_d2,

#                 # Food 1 location for snake 2
#                 game.food1.x < game.head2.x, # Food 1 is left of snake 2
#                 game.food1.x > game.head2.x, # Food 1 is right of snake 2
#                 game.food1.y < game.head2.y, # Food 1 is up of snake 2
#                 game.food1.y > game.head2.y, # Food 1 is down of snake 2

#                 # Food 2 location for snake 2
#                 game.food2.x < game.head2.x, # Food 2 is left of snake 2
#                 game.food2.x > game.head2.x, # Food 2 is right of snake 2
#                 game.food2.y < game.head2.y, # Food 2 is up of snake 2
#                 game.food2.y > game.head2.y, # Food 2 is down of snake 2
#             ]
        # state = [
        #     # Danger straight snake 1
        #     (dir_r1 and game.is_collision(point_r1)) or 
        #     (dir_l1 and game.is_collision(point_l1)) or 
        #     (dir_u1 and game.is_collision(point_u1)) or 
        #     (dir_d1 and game.is_collision(point_d1)), 

        #     # Danger straight snake 2
        #     (dir_r2 and game.is_collision(point_r2)) or 
        #     (dir_l2 and game.is_collision(point_l2)) or 
        #     (dir_u2 and game.is_collision(point_u2)) or 
        #     (dir_d2 and game.is_collision(point_d2)), 

        #     # Danger right snake 1
        #     (dir_r1 and game.is_collision(point_d1)) or 
        #     (dir_l1 and game.is_collision(point_u1)) or 
        #     (dir_u1 and game.is_collision(point_r1)) or 
        #     (dir_d1 and game.is_collision(point_l1)), 

        #     # Danger right snake 2
        #     (dir_r2 and game.is_collision(point_d2)) or 
        #     (dir_l2 and game.is_collision(point_u2)) or 
        #     (dir_u2 and game.is_collision(point_r2)) or 
        #     (dir_d2 and game.is_collision(point_l2)), 

        #     # Danger left snake 1
        #     (dir_r1 and game.is_collision(point_u1)) or
        #     (dir_l1 and game.is_collision(point_d1)) or
        #     (dir_u1 and game.is_collision(point_l1)) or
        #     (dir_d1 and game.is_collision(point_r1)),

        #     # Danger left snake 2
        #     (dir_r2 and game.is_collision(point_u2)) or
        #     (dir_l2 and game.is_collision(point_d2)) or
        #     (dir_u2 and game.is_collision(point_l2)) or
        #     (dir_d2 and game.is_collision(point_r2)),

        #     # Move direction snake 1(only one should be true)
        #     dir_l1, 
        #     dir_r1, 
        #     dir_u1, 
        #     dir_d1,

        #     # Move direction snake 2
        #     dir_l2, 
        #     dir_r2, 
        #     dir_u2, 
        #     dir_d2,

        #     # Food 1 location for snake 1
        #     game.food1.x < game.head1.x, # Food 1 is left of snake 1
        #     game.food1.x > game.head1.x, # Food 1 is right of snake 1
        #     game.food1.y < game.head1.y, # Food 1 is up of snake 1
        #     game.food1.y > game.head1.y, # Food 1 is down of snake 1

        #     # Food 2 location for snake 1
        #     game.food2.x < game.head1.x, # Food 2 is left of snake 1
        #     game.food2.x > game.head1.x, # Food 2 is right of snake 1
        #     game.food2.y < game.head1.y, # Food 2 is up of snake 1
        #     game.food2.y > game.head1.y, # Food 2 is down of snake 1

        #     # Food 1 location for snake 2
        #     game.food1.x < game.head2.x, # Food 1 is left of snake 2
        #     game.food1.x > game.head2.x, # Food 1 is right of snake 2
        #     game.food1.y < game.head2.y, # Food 1 is up of snake 2
        #     game.food1.y > game.head2.y, # Food 1 is down of snake 2

        #     # Food 2 location for snake 2
        #     game.food2.x < game.head2.x, # Food 2 is left of snake 2
        #     game.food2.x > game.head2.x, # Food 2 is right of snake 2
        #     game.food2.y < game.head2.y, # Food 2 is up of snake 2
        #     game.food2.y > game.head2.y, # Food 2 is down of snake 2
        # ]

#         return np.array(state, dtype = int)



#     def remember(self, state, action, reward, next_state, game_over):
#         self.memory.append((state, action, reward, next_state, game_over)) # Popleft if MAX_MEMORY is reached



#     def train_long_memory(self, other_model):
#         if len(self.memory) > BATCH_SIZE:
#             memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
#         else:
#             memory_sample = self.memory

#         states, actions, rewards, next_states, game_overs = zip(*memory_sample)
#         self.trainer.train_step(states, actions, rewards, next_states, game_overs, other_model)


#     def prepare_long_memory_train(self):
#         if len(self.memory) > BATCH_SIZE:
#             memory_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
#         else:
#             memory_sample = self.memory

#         states, actions, rewards, next_states, game_overs = zip(*memory_sample)

#         return states, actions, rewards, next_states, game_overs
    

#     def train_long_memory_v2(self, total_states, total_actions, total_rewards, total_next_states, total_game_overs):
#         self.trainer.train_step(total_states, total_actions, total_rewards, total_next_states, total_game_overs)


#     def train_short_memory(self, state, action, reward, next_state, game_over, other_model):
#         self.trainer.train_step(state, action, reward, next_state, game_over, other_model) # Train for a single step



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
#     agent1 = Agent()
#     agent2 = Agent()
#     combined_Learning = Combination(agent1.model, agent2.model)
#     game = SnakeGameAI()
#     gamma = 0.9
#     model = Linear_QNet(15, 256, 3) # input is size of states, output is size of action
#     trainer = QTrainer(model, lr = lr, gamma = gamma, model_long = combined_Learning)

#     while True:
#         # get old state
#         old_state1 = agent1.get_state(game, True)
#         old_state2 = agent2.get_state(game, False)

#         # get move (or action)
#         final_move1 = agent1.get_action(old_state1)
#         final_move2 = agent2.get_action(old_state2)

#         # perform move and get new state
#         reward, game_over, score = game.play_step(final_move1, final_move2)
#         new_state1 = agent1.get_state(game, True)
#         new_state2 = agent2.get_state(game, False)
#         # train short memory (one step)
#         agent1.train_short_memory(old_state1, final_move1, reward, new_state1, game_over, '2')
#         agent2.train_short_memory(old_state2, final_move2, reward, new_state2, game_over, '1')

#         # remember
#         agent1.remember(old_state1, final_move1, reward, new_state1, game_over)
#         agent2.remember(old_state2, final_move2, reward, new_state2, game_over)

#         if game_over:
#             # train long memory (or replay memory) and plot result
#             game.reset()
#             agent1.n_games += 1
#             agent2.n_games = agent1.n_games
#             # states1, actions1, rewards1, next_states1, game_overs1 = agent1.prepare_long_memory_train()
#             # states2, actions2, rewards2, next_states2, game_overs2 = agent2.prepare_long_memory_train()
#             agent1.train_long_memory('2')
#             agent2.train_long_memory('1')
#             # total_states = states1 + states2
#             # total_actions = actions1 + actions2
#             # total_rewards = rewards1 + rewards2
#             # total_next_states = next_states1 + next_states2
#             # total_game_overs = game_overs1 + game_overs2

#             # agent1.train_long_memory_v2(total_states, total_actions, total_rewards, total_next_states, total_game_overs)
#             # agent2.train_long_memory_v2(total_states, total_actions, total_rewards, total_next_states, total_game_overs)
#             #trainer.train_step(total_states, total_actions, total_rewards, total_next_states, total_game_overs)

#             #trainer.train_long_step(states1, actions1, rewards1, next_states1, game_overs1, states2, actions2, rewards2, next_states2, game_overs2)

#             if score > record:
#                 record = score
#                 agent1.model.save('model1.pth') 
#                 agent2.model.save('model2.pth')
            
#             print('Game ', agent1.n_games, 'Score ', score, "Record ", record)

#             plot_scores.append(score)
#             total_score += score
#             mean_score = total_score / agent1.n_games
#             plot_mean_scores.append(mean_score)
#             plot(plot_scores, plot_mean_scores)


# if __name__ == '__main__':
#     train()
