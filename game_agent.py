# this class is used to create an implementation of the game for an agent
# implementing base game
import pygame
import numpy as np
import random
from enum import Enum # defining directions right away
from collections import namedtuple

# parts of the game
# the background: rendered by pygame.display
# directions: left, right, up and down
# parts of the snake, appending a snake head every time it gets food
# food: putting food in random coordinates
# game mechanic loop: 
# 1. spawn snake head in the middle of the screen
# 2. spawn random food
# 3. keep moving snake every frame in direction, unless changed
# 4. get keystrokes, change direction based on keystrokes
# 5. move the snake every frame of the game
# 6. every time food is consumed, replace snake head with new head
# 7. if snake hits walls or itself, game over


# initialize the game
pygame.init()
font = pygame.font.SysFont('Arial', 20)

# make enum for directions for convenience
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# initialize simple class point for better readability
Point = namedtuple('Point', 'x, y')

# store rgb values for convenience
RED = (255,0,0)
PINK = (255,20,147)
HOT_PINK = (255, 105, 180)
PEACH = (253,201,186)
BLUE1 = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

# setting constraints
BLOCK = 20
SPEED = 80

# main snake game class
class SnakeGameAgent:
    def __init__(self, h=480, w=640):
        self.h = h
        self.w = w
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("SNAKE GAME AGENT")
        pygame.display.update()
        self.clock = pygame.time.Clock()
        self.reset()
    
    def reset(self):
        # initialize game state
        self.snake_direction = Direction.RIGHT
        self.snake_head = Point(self.w / 2, self.h / 2)
        self.snake_body = [self.snake_head, Point(self.snake_head.x - BLOCK, self.snake_head.y), Point(self.snake_head.x - (2*BLOCK), self.snake_head.y)]
        self.food = None 
        self.score = 0
        self.place_food_randomly()
        self.game_over = False
        self.nframes = 0


    def place_food_randomly(self):
        # create new coordinates for food 
        # multiply by block to get actual coordinates on display
        x = random.randint(0, (self.w - BLOCK) // BLOCK) * BLOCK 
        y = random.randint(0, (self.h - BLOCK) // BLOCK) * BLOCK

        self.food = Point(x,y)

        # check if food has spawned on snake
        if self.food in self.snake_body:
            self.place_food_randomly()
    
    # this function gets input from the user and does one step ahead,
    # checks for collisions, checks for food consumption, updates score
    # places food again if consumed, exits game if lost
    def make_a_step(self, direction_vector):
        # initialize reward
        reward = -1
        self.nframes += 1
        # check events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                return self.game_over
        # remove keypress implementation with agent predictions
        # directions = [RIGHT, DOWN, LEFT, UP]
        if direction_vector == [1, 0, 0]:  # Keep moving straight
            pass  # No need to change direction
        elif direction_vector == [0, 1, 0]:  # Turn left
            if self.snake_direction == Direction.UP:
                self.snake_direction = Direction.LEFT
            elif self.snake_direction == Direction.LEFT:
                self.snake_direction = Direction.DOWN
            elif self.snake_direction == Direction.DOWN:
                self.snake_direction = Direction.RIGHT
            elif self.snake_direction == Direction.RIGHT:
                self.snake_direction = Direction.UP
        elif direction_vector == [0, 0, 1]:  # Turn right
            if self.snake_direction == Direction.UP:
                self.snake_direction = Direction.RIGHT
            elif self.snake_direction == Direction.RIGHT:
                self.snake_direction = Direction.DOWN
            elif self.snake_direction == Direction.DOWN:
                self.snake_direction = Direction.LEFT
            elif self.snake_direction == Direction.LEFT:
                self.snake_direction = Direction.UP
        # once we have the new direction, we move the snake one block
        self.move_snake()
        # insert new head into snake's body once moved 
        self.snake_body.insert(0, self.snake_head)

        # check for collisions or frame iterations
        if self.check_collision() or self.nframes > 100 * len(self.snake_body):
            self.game_over = True
            reward = -10 
            return reward, self.game_over

        # check if snake just ate food
        if self.snake_head == self.food:
            self.score += 1
            reward = 30
            self.place_food_randomly()
        else:
            self.snake_body.pop() # just a normal turn and no food consumed
        
        # once all checks are done, update ui to reflect move
        self.update_ui()
        self.clock.tick(SPEED)

        return reward, self.game_over



    def move_snake(self):
        x,y = self.snake_head.x, self.snake_head.y
        if self.snake_direction == Direction.LEFT:
            x -= BLOCK
        elif self.snake_direction == Direction.RIGHT:
            x += BLOCK 
        elif self.snake_direction == Direction.DOWN:
            y += BLOCK
        else:
            y -= BLOCK
        
        new_head = Point(x,y)
        self.snake_head = new_head
        
        

    def check_collision(self, point = None):
        if point is None:
            point = self.snake_head
        # check collision using self.snake_head
        if point.x > self.w - BLOCK or point.x < 0 or point.y  < 0 or point.y > self.h - BLOCK:
            self.game_over = True
            return True
        
        # check if snake collided with itself 
        if point in self.snake_body[1:]: # first point in body is head
            self.game_over = True
            return True
        return False
    



    def update_ui(self):
        self.display.fill(BLACK) # fill display with black
        # draw every point of the snake
        for part in self.snake_body:
            pygame.draw.rect(self.display, PINK, pygame.Rect(part.x, part.y, BLOCK, BLOCK))
            pygame.draw.rect(self.display, HOT_PINK, pygame.Rect(part.x+4, part.y+4, 12, 12))
        
        # draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK, BLOCK))

        # write score near the top left 
        score_text = font.render(f"Score: {self.score}", True, BLUE1)
        self.display.blit(score_text, [10, 10])
        # flip the screen to reflect changes
        pygame.display.flip()
    
    def end_game(self):
        if self.game_over == True:
            pygame.quit()
            quit()
                    
