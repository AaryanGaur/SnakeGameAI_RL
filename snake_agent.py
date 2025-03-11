# this class manages the agent functionality for the snake game ai
# this agent uses the bellman equation to calculate Q values
import torch
import numpy as np
import random 
from enum import Enum
from game_agent import SnakeGameAgent, Point
from collections import deque # for long term memory storage
from trainer import QTrainer
from model import QNet

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# possible actions and other set values
POSSIBLE = [[1,0,0], [0,1,0], [0,0,1]] # go straight, take a left, take a right
BATCH_SIZE = 1000

class Agent:
    def __init__(self):
        self.n_games = 0 # records total number of games
        self.epsilon = 0 # randomness factor
        self.gamma = 0.9 # discount factor meaning importance of future rewards
        self.memory = deque(maxlen=100_000)
        self.model = QNet(11, 256, 3)
        self.learning_rate = 0.001
        self.trainer = QTrainer(self.gamma, self.learning_rate, self.model)

        # set epsilon decay parameters
        self.epsilon_min = 0.1 # it should have some randomness at least
        self.epsilon_decay_rate = 0.99 # decay rate
    
    # updating epsilon using a moderate decay rate
    def update_epsilon(self):
        # decay epsilon gradually to reduce exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay_rate
        else:
            self.epsilon = self.epsilon_min

    # get current game state
    def get_game_state(self, game):
        # state will look like this -
        # state = [danger down, danger right, danger left,
        # danger up, food left, food down, food right, food up, 
        # manhattan x distance, manhattan y distance
        head = game.snake_body[0] # current snake head 
        # checking danger points
        point_left = Point(head.x-20, head.y)
        point_right = Point(head.x+20, head.y)
        point_down = Point(head.x, head.y+20)
        point_up = Point(head.x, head.y-20)

        # get abs distance of food
        # dis_x = abs(head.x - game.food.x)
        # dis_y = abs(head.y - game.food.y)

        # get current direction of snake as a set of booleans
        direction_r = game.snake_direction == Direction.RIGHT
        direction_d = game.snake_direction == Direction.DOWN
        direction_l = game.snake_direction == Direction.LEFT
        direction_u = game.snake_direction == Direction.UP

        # create state 
        state = [
            # check where the danger is
            # if danger is in the same direction as snake head 
            (direction_r and game.check_collision(point_right)) or
            (direction_l and game.check_collision(point_left)) or 
            (direction_d and game.check_collision(point_down)) or 
            (direction_u and game.check_collision(point_up)),

            # check if danger is to the right
            (direction_r and game.check_collision(point_down)) or
            (direction_d and game.check_collision(point_left)) or
            (direction_l and game.check_collision(point_up)) or
            (direction_u and game.check_collision(point_right)),

            # check if danger is to the left 
            (direction_r and game.check_collision(point_up)) or
            (direction_d and game.check_collision(point_right)) or
            (direction_l and game.check_collision(point_down)) or
            (direction_u and game.check_collision(point_left)),

            # snake direction
            direction_l,
            direction_r,
            direction_d,
            direction_u,

            # check food placement
            game.snake_head.x > game.food.x, # left check
            game.snake_head.x < game.food.x, # right check
            game.snake_head.y > game.food.y, # down check
            game.snake_head.y < game.food.y, # up check

        ]

        return np.array(state, dtype = int) # return state for forward feed network
    
    # get move from our agent
    def get_move(self, game):
        # exploration vs exploitation
        # get game state first 
        final = [0,0,0]
        state = self.get_game_state(game)
        self.epsilon = 80 - self.n_games

        # get random probability value 
        if random.randint(0,200) < self.epsilon:
            # exploration: random action
            random_move = random.randint(0,2)
            final[random_move] = 1
            move = final
        else:
            # exploitation: making best move according to neural network
            state_tensor = torch.tensor(state, dtype=torch.float)

            # make prediction and get q values for all possible actions
            q_values = self.model(state_tensor)

            # get best action
            best_action_index = torch.argmax(q_values).item()

            # return best move 
            final[best_action_index] = 1
            move = final
        
        # return final move 
        return move

    # add an experience to memory
    def add_experience(self, state, action, reward, next_state, done):
        self.memory.append((state,action,reward, next_state, done))

    # the experience replay function
    def experience_replay(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.experienced_learning(states, actions, rewards, next_states, dones)

    def quick_memory(self, state, action, reward, next_state, done):
        self.trainer.experienced_learning(state, action, reward, next_state, done)


    # placeholder function
    '''def get_move(self, snake_game):
        # definition of directions
        # [0,1,2,3] -> RIGHT, LEFT, UP, DOWN
        # debugging
        ret = POSSIBLE[self.index % 4]
        self.index+=1
        return ret'''
    

# define run function
def run():
    # initialize record 
    record = 0
    # initialize game and agent
    agent = Agent()
    game = SnakeGameAgent()

    while True:
        # get current game state
        current_state = agent.get_game_state(game)

        # decide next move 
        move = agent.get_move(game)

        # get reward and game_over values 
        reward, done = game.make_a_step(move)

        # once made the move, get new state 
        new_state = agent.get_game_state(game)

        # train short term memory
        agent.quick_memory(current_state, move, reward, new_state, done)

        # add experience to memory
        agent.add_experience(current_state, move, reward, new_state, done)

        # If game is over, reset and update exploration
        if done:
            score = game.score
            game.reset()
            agent.n_games += 1
            agent.experience_replay()
            if score > record:
                record = score
            print(f"Game {agent.n_games} - Score: {score} - Record: {record}")

# finally.....
run()
