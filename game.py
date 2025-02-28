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
SPEED = 5

# main snake game class
class SnakeGame:
    def __init__(self, h=480, w=640):
        self.h = h
        self.w = w
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("SNAKE GAME")
        self.clock = pygame.time.Clock()
        self.snake_direction = Direction.RIGHT
        self.game_over = False
        # initialize the snake
        self.snake_head = Point(self.w // 2, self.h // 2)
        self.snake_body = [self.snake_head, Point(self.snake_head.x - BLOCK, self.snake_head.y), Point(self.snake_head.x - (2*BLOCK), self.snake_head.y)]
        self.food = None 
        self.score = 0
        self.place_food_randomly()

    def place_food_randomly(self):
        # create new coordinates for food 
        # multiply by block to get actual coordinates on display
        x = random.randint(0, (self.w // BLOCK) - 1) * BLOCK 
        y = random.randint(0, (self.h // BLOCK) - 1) * BLOCK

        self.food = Point(x,y)

        # check if food has spawned on snake
        if self.food in self.snake_body:
            self.place_food_randomly()
    
    # this function gets input from the user and does one step ahead,
    # checks for collisions, checks for food consumption, updates score
    # places food again if consumed, exits game if lost
    def make_a_step(self):
        #current_direction = self.snake_direction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                return self.game_over
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.snake_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.snake_direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.snake_direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.snake_direction = Direction.DOWN
        
        # once we have the new direction, we move the snake one block
        self.move_snake()
        # insert new head into snake's body once moved 
        self.snake_body.insert(0, self.snake_head)

        # check if there has been a collision
        self.check_collision()
        # check if game is over 
        if self.game_over:
            return self.game_over

        # check if snake just ate food
        if self.snake_head == self.food:
            self.score += 1
            self.place_food_randomly()
        else:
            self.snake_body.pop() # just a normal turn and no food consumed
        
        # once all checks are done, update ui to reflect move
        self.update_ui()
        self.clock.tick(SPEED)

        return self.game_over



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
        
        

    def check_collision(self):
        # check collision using self.snake_head
        if self.snake_head.x > self.w - BLOCK or self.snake_head.x < 0 or self.snake_head.y  < 0 or self.snake_head.y > self.h - BLOCK:
            self.game_over = True
        
        # check if snake collided with itself 
        if self.snake_head in self.snake_body[1:]: # first point in body is head
            self.game_over = True


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


    # testing 
    '''
    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                
                # for testing purposes, fill screen with pink
                self.display.fill(PINK)
                pygame.display.flip()
                self.clock.tick(SPEED)
        pygame.display.quit()
        pygame.quit()'''
                    


# main game loop
game = SnakeGame()
while True:
    done = game.make_a_step()
    if done == True:
        break


pygame.quit()
    
