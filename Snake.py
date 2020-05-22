import pygame
from pygame.locals import *
import sys, os
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
    def __init__(self, grid):
        self.x, self.y = 0, 0
        self.reset_position(grid)


    def draw(self, window):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(window, (255,0,0), rect)

    def reset_position(self, grid):
        grid[self.x][self.y] = 'X' #Apple will move, replace in grid
        valid_pos = False
        while not valid_pos:
            self.x = random.randint(0,GRID_SIZE - 1)
            self.y = random.randint(0,GRID_SIZE - 1)
            if grid[self.x][self.y] != 'S': #Check to ensure apple doesn't spawn on the snake
                grid[self.x][self.y] = 'A'
                valid_pos = True

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
            self.y = GRID_SIZE - 1 if self.y <=0 else self.y - 1
        elif direction == Direction.DOWN:
            self.y = 0 if self.y >= GRID_SIZE - 1 else self.y + 1
        elif direction == Direction.LEFT:
            self.x = GRID_SIZE - 1 if self.x <= 0 else self.x - 1
        else:
            self.x = 0 if self.x >= GRID_SIZE - 1 else self.x + 1

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window, gradient):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        red = int(5 + 25 * gradient)
        green = int(50 + 205 * gradient)
        blue = int(10 + 50 * gradient)
        pygame.draw.rect(window, (red, green, blue), rect)
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
        count = 1
        self.head.draw(window, count/(len(self.body) + 1))
        for segment in self.body:
            count+=1
            segment.draw(window, count/(len(self.body) + 1))

    def set_direction(self, direction):
        if direction == Direction.UP and self.direction == Direction.DOWN or self.direction == Direction.UP and direction == Direction.DOWN:
            return
        if direction == Direction.LEFT and self.direction == Direction.RIGHT or self.direction == Direction.LEFT and direction == Direction.RIGHT:
            return
        self.direction = direction

    def add(self):
        self.queue += 1

    def move(self, grid):
        x, y = self.head.get_x(), self.head.get_y()
        grid[x][y] = 'X'
        self.head.move(self.direction)
        grid[self.head.get_x()][self.head.get_y()] = 'S'
        #When a snake eats an apple, a segment is added to the queue to be added in the next movement tick
        if self.queue > 0:
            self.body.insert(0,SnakeSegment(x, y))
            self.queue -= 1
            return

        for segment in self.body:
            temp_x,temp_y = segment.get_x(),segment.get_y()
            grid[temp_x][temp_y] = 'X'
            segment.move_to(x, y)
            grid[x][y] = 'S'
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
        self.min_move_time = 90
        pygame.time.set_timer(self.MOVE_SNAKE, self.move_time)

        #Game map/grid
        self.show_grid = False
        self.grid = [['X' for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]

        self.snake = Snake(int(GRID_SIZE/2), int(GRID_SIZE/2))
        self.apple = Apple(self.grid)

        #Font
        self.font = pygame.font.SysFont(None,30)
        self.score = 0
        self.highscore = 0
        with open("highscore.txt", "r") as save_data:
            data = save_data.read()
            self.highscore = int(data) if data else self.highscore
        self.score_label = self.font.render("SCORE: " + str(self.score), 1, (0,0,0))
        self.highscore_label = self.font.render("HIGHSCORE: " + str(self.highscore), 1, (190,0,0))

    def has_snake_eaten_apple(self):
        return (self.snake.get_head_x() == self.apple.get_x()) and (self.snake.get_head_y() == self.apple.get_y())

    def update_score(self):
        self.score += 1
        self.score_label = self.font.render("SCORE: " + str(self.score), 1, (0,0,0))
        if self.score >= self.highscore:
            self.highscore = self.score
            self.highscore_label = self.font.render("HIGHSCORE: " + str(self.highscore), 1, (0,0,0))

    def handle_events(self):
        #Check if user closes the game
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYUP:
                if event.key == K_UP:
                    self.snake.set_direction(Direction.UP)
                elif event.key == K_DOWN:
                    self.snake.set_direction(Direction.DOWN)
                elif event.key == K_LEFT:
                    self.snake.set_direction(Direction.LEFT)
                elif event.key == K_RIGHT:
                    self.snake.set_direction(Direction.RIGHT)
                elif event.key == K_g:
                    self.show_grid = not self.show_grid
            if event.type == self.MOVE_SNAKE:
                self.snake.move(self.grid)
                self.running = not self.snake.has_collision_occured()
                if not self.running:
                    self.end_game()
                if self.has_snake_eaten_apple():
                    self.snake.add()
                    self.apple.reset_position(self.grid)
                    #Update the score
                    self.update_score()
                    #Speed up the snake
                    self.move_time -= 1
                    pygame.time.set_timer(self.MOVE_SNAKE, max(self.move_time, self.min_move_time))


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

        #Display score
        self.window.blit(self.score_label, (WINDOW_SIZE - self.score_label.get_width() - 10, 10))
        self.window.blit(self.highscore_label, (WINDOW_SIZE - self.highscore_label.get_width() - self.score_label.get_width() - 10 * 2, 10))
        pygame.display.flip()

    #Called when the snake dies
    def end_game(self):
        if self.score >= self.highscore:
            with open("highscore.txt", "w") as save_data:
                save_data.write(str(self.score))


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
#If save data file does not exists (i.e first time running or deleted), create a new file
if not os.path.exists("highscore.txt"):
    with open("highscore.txt", "w"): pass
game.run()
