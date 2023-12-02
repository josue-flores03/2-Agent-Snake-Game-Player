import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module): 
    
    def __init__(self, input_size, hidden_size, hidden_size_2, output_size):
        super().__init__()
        self.linear_1 = nn.Linear(input_size, hidden_size)
        self.linear_2 = nn.Linear(hidden_size, hidden_size_2)
        self.linear_3 = nn.Linear(hidden_size_2, output_size)



    def forward(self, x):
        x = F.relu(self.linear_1(x))
        x = F.relu(self.linear_2(x))
        x = self.linear_3(x)
        return x
    


    def save(self, file_name = 'model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)



class QTrainer:

    def __init__(self, model1, lr, gamma, model_long = None):
        self.lr = lr
        self.gamma = gamma
        self.model = model1
        self.alpha = 0.1
        self.optimizer = optim.Adam(model1.parameters(), lr = self.lr)
        self.criterion = nn.MSELoss()



    def train_step(self, state, action, reward, next_state, game_over, model_2, other_model_path = None):
        state = torch.tensor(state, dtype = torch.float)
        next_state = torch.tensor(next_state, dtype = torch.float)
        action = torch.tensor(action, dtype = torch.long)
        reward = torch.tensor(reward, dtype = torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            game_over = (game_over, )
        
        # Get predicted Q values with current states
        pred = self.model(state)

        # Get predicted Q values with next states
        target = pred.clone()
        for idx in range(len(game_over)):
            Q_new = reward[idx]
            if not game_over[idx]:
                    Q_new = Q_new + self.alpha * (reward[idx] + self.gamma * torch.max(model_2(next_state[idx])) - torch.max(self.model(state[idx])))

            target[idx][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

    

    def  train_long_step(self, state1, action1, reward1, next_state1, game_over1, state2, action2, reward2, next_state2, game_over2):        
        state1 = torch.tensor(state1, dtype = torch.float)
        next_state1 = torch.tensor(next_state1, dtype = torch.float)
        action1 = torch.tensor(action1, dtype = torch.long)
        reward1 = torch.tensor(reward1, dtype = torch.float)

        state2 = torch.tensor(state2, dtype = torch.float)
        next_state2 = torch.tensor(next_state2, dtype = torch.float)
        action2 = torch.tensor(action2, dtype = torch.long)
        reward2 = torch.tensor(reward2, dtype = torch.float)

        if len(state1.shape) == 1:
            state1 = torch.unsqueeze(state1, 0)
            next_state1 = torch.unsqueeze(next_state1, 0)
            action1 = torch.unsqueeze(action1, 0)
            reward1 = torch.unsqueeze(reward1, 0)
            game_over1 = (game_over1, )

            state2 = torch.unsqueeze(state2, 0)
            next_state2 = torch.unsqueeze(next_state2, 0)
            action2 = torch.unsqueeze(action2, 0)
            reward2 = torch.unsqueeze(reward2, 0)
            game_over2 = (game_over2, )
        
        # Get predicted Q values with current states
        pred = self.model_long(state1, state2)
        # Get predicted Q values with next states
        target = pred.clone() + pred.clone()
        idx = 0
        for idx in range(len(game_over1)):
            Q_new = reward1[idx]
            if not game_over1[idx]:
                Q_new = reward1[idx] + self.gamma * torch.max(self.model(next_state1[idx]))

            target[idx][torch.argmax(action1).item()] = Q_new


        for idx in range(len(game_over2)):
            Q_new = reward2[idx]
            if not game_over2[idx]:
                Q_new = reward2[idx] + self.gamma * torch.max(self.model(next_state2[idx]))
            target[idx][torch.argmax(action2).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward(retain_graph=True)

        self.optimizer.step()
        


class Combination(nn.Module):
    def __init__(self, agent1_model, agent2_model):
        super(Combination, self).__init__()
        self.agent1_model = agent1_model
        self.agent2_model = agent2_model
        self.classifier = nn.Linear(6, 3)
        
    def forward(self, x1, x2):
        x1 = self.agent1_model(x1)
        x2 = self.agent2_model(x2)
        x = torch.cat((x1, x2), dim=1)
        x = self.classifier(F.relu(x))
        return x
    