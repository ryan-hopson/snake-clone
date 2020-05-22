import pygame
from pygame.locals import *
import sys
import time
import random

WINDOW_SIZE = 640
GRID_SIZE = 20
CELL_SIZE = WINDOW_SIZE/GRID_SIZE

class Direction:
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3

class Apple:
    def __init__(self):
        self.reset_position()

    def draw(self, window):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(window, (255,0,0), rect)

    def reset_position(self):
        self.x = random.randint(0,GRID_SIZE - 1)
        self.y = random.randint(0,GRID_SIZE - 1)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class SnakeSegment:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, direction):
        if direction == Direction.UP:
            self.y = self.y - 1
        elif direction == Direction.DOWN:
            self.y = self.y + 1
        elif direction == Direction.LEFT:
            self.x = self.x - 1
        else:
            self.x = self.x + 1

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(window, (30,255,60), rect)
        pygame.draw.rect(window, (255,255,255), rect, 1)

    def check_collison(self, segment):
        return self.x == segment.get_x() and self.y == segment.get_y()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class Snake:
    def __init__(self, x, y):
        self.direction = Direction.UP
        self.body = []
        self.queue = 0 #Holds segments that need to be added
        self.head = SnakeSegment(x,y)

    def update(self):
        self.move()

    def draw(self, window):
        self.head.draw(window)
        for segment in self.body:
            segment.draw(window)

    def set_direction(self, direction):
        if direction == Direction.UP and self.direction == Direction.DOWN or self.direction == Direction.UP and direction == Direction.DOWN:
            return False
        if direction == Direction.LEFT and self.direction == Direction.RIGHT or self.direction == Direction.LEFT and direction == Direction.RIGHT:
            return False
        self.direction = direction
        return True

    def add(self):
        self.queue += 1

    def move(self):
        x, y = self.head.get_x(), self.head.get_y()
        self.head.move(self.direction)
        #When a snake eats an apple, a segment is added to the queue to be added in the next movement tick
        if self.queue > 0:
            self.body.insert(0,SnakeSegment(x, y))
            self.queue -= 1
            return

        for segment in self.body:
            temp_x,temp_y = segment.get_x(),segment.get_y()
            segment.move_to(x, y)
            x,y = temp_x,temp_y

    def has_collision_occured(self):
        for segment in self.body:
            if segment.check_collison(self.head):
                return True
        return False

    def get_head_x(self):
        return self.head.get_x()

    def get_head_y(self):
        return self.head.get_y()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~         GRID FORMAT          ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~        +-----------+         ~
# ~        | X X X X X |         ~
# ~        | X X X H X |         ~
# ~        | X T X B X |         ~
# ~        | X B B B X |         ~
# ~        | X X X X X |         ~
# ~        +-----------+         ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~            Key               ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~ H - Head, B - Body, T - Tail ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("SnakeClone")
        self.window = pygame.display.set_mode((WINDOW_SIZE,WINDOW_SIZE))
        self.running = True

        self.clock = pygame.time.Clock()

        self.MOVE_SNAKE = pygame.USEREVENT+1
        self.move_time = 120
        #TODO: Add upper/lower bounds to snake movement speed
        pygame.time.set_timer(self.MOVE_SNAKE, self.move_time)

        self.snake = Snake(GRID_SIZE/2, GRID_SIZE/2)
        self.apple = Apple()

        self.show_grid = False

    def has_snake_eaten_apple(self):
        return (self.snake.get_head_x() == self.apple.get_x()) and (self.snake.get_head_y() == self.apple.get_y())

    def handle_events(self):
        has_changed_direction = False
        #Check if user closes the game
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYUP:
                if event.key == K_UP:
                    has_changed_direction = self.snake.set_direction(Direction.UP)
                elif event.key == K_DOWN:
                    has_changed_direction = self.snake.set_direction(Direction.DOWN)
                elif event.key == K_LEFT:
                    has_changed_direction = self.snake.set_direction(Direction.LEFT)
                elif event.key == K_RIGHT:
                    has_changed_direction = self.snake.set_direction(Direction.RIGHT)
                elif event.key == K_g:
                    self.show_grid = not self.show_grid
            if event.type == self.MOVE_SNAKE or has_changed_direction: #Trigger with a key press
                pygame.time.set_timer(self.MOVE_SNAKE, 0)
                pygame.time.set_timer(self.MOVE_SNAKE, self.move_time) #Reset timer
                self.snake.move()
                self.running = not self.snake.has_collision_occured()
                if self.has_snake_eaten_apple():
                    self.snake.add()
                    self.apple.reset_position()

    def draw_grid(self, window):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.window, (0,0,0), rect, 1)

    def draw(self):
        self.window.fill((255,255,255))
        if self.show_grid:
            self.draw_grid()
        self.snake.draw(self.window)
        self.apple.draw(self.window)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)
        print("Quitting applciation")
        pygame.display.quit()
        pygame.quit()
        sys.exit(0)

game = Game()
game.run()
