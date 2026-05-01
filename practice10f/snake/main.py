import pygame
from color_palette import *
import random

pygame.init()

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

CELL = 30

# These variables are required by the task
SCORE = 0
LEVEL = 1
FPS = 5

font = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 50)


def draw_grid():
    # Draws simple grid like in lecture notes
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"


class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.grow = False

    def move(self):
        # Save last tail position. If snake eats food, new segment appears here.
        tail = Point(self.body[-1].x, self.body[-1].y)

        # Move body from tail to head
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        # Move head
        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # If food was eaten, add one segment to the old tail position
        if self.grow:
            self.body.append(tail)
            self.grow = False

    def draw(self):
        # Head is red, body is yellow
        head = self.body[0]
        pygame.draw.rect(screen, colorRED, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_food_collision(self, food):
        global SCORE, LEVEL, FPS

        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            # Snake should grow after eating food
            self.grow = True
            SCORE += 1

            # Every 3 foods level increases and snake becomes faster
            if SCORE % 3 == 0:
                LEVEL += 1
                FPS += 2

            food.generate_random_pos(self)

    def check_wall_collision(self):
        head = self.body[0]
        if head.x < 0 or head.x >= WIDTH // CELL:
            return True
        if head.y < 0 or head.y >= HEIGHT // CELL:
            return True
        return False

    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True
        return False


class Food:
    def __init__(self):
        self.pos = Point(9, 9)

    def draw(self):
        pygame.draw.rect(screen, colorGREEN, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    def generate_random_pos(self, snake):
        # Food must not appear on the snake body
        while True:
            x = random.randint(0, WIDTH // CELL - 1)
            y = random.randint(0, HEIGHT // CELL - 1)

            on_snake = False
            for segment in snake.body:
                if segment.x == x and segment.y == y:
                    on_snake = True
                    break

            if not on_snake:
                self.pos.x = x
                self.pos.y = y
                break


clock = pygame.time.Clock()
food = Food()
snake = Snake()
food.generate_random_pos(snake)

running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Direction cannot be changed directly backwards
            if event.key == pygame.K_RIGHT and snake.dx != -1:
                snake.dx = 1
                snake.dy = 0
            elif event.key == pygame.K_LEFT and snake.dx != 1:
                snake.dx = -1
                snake.dy = 0
            elif event.key == pygame.K_DOWN and snake.dy != -1:
                snake.dx = 0
                snake.dy = 1
            elif event.key == pygame.K_UP and snake.dy != 1:
                snake.dx = 0
                snake.dy = -1

    if not game_over:
        screen.fill(colorBLACK)
        draw_grid()

        snake.move()
        snake.check_food_collision(food)

        # Game ends only if snake hits wall or itself
        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True

        snake.draw()
        food.draw()

        score_text = font.render("Score: " + str(SCORE), True, colorWHITE)
        level_text = font.render("Level: " + str(LEVEL), True, colorWHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 35))
    else:
        screen.fill(colorBLACK)
        text = font_big.render("Game Over", True, colorRED)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
