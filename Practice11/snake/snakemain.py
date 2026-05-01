import pygame
from color_palette import *
import random

pygame.init()

WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

CELL = 30

# Score, level and speed — required by the task
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

    def check_food_collision(self, food_list):
        """
        Check collision against every food in food_list.
        Returns the Food object that was eaten, or None.
        """
        global SCORE, LEVEL, FPS

        head = self.body[0]
        for food in food_list:
            if head.x == food.pos.x and head.y == food.pos.y:
                self.grow = True
                SCORE += food.value  # add food's weight/value to score

                # Every 3 score points level increases and snake becomes faster
                if SCORE % 3 == 0:
                    LEVEL += 1
                    FPS += 2

                return food  # caller removes this food and spawns a new one
        return None

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
    """
    Food with a random weight (value) and a countdown timer.

    Weight table (chosen randomly on each spawn):
      - value 1: 60% chance — green (normal)
      - value 2: 30% chance — blue  (bonus)
      - value 3: 10% chance — white (rare)

    Each food disappears after LIFETIME game ticks if not eaten.
    Rarer foods disappear faster.
    """

    FOOD_TYPES = [
        # (value, probability, color, lifetime_ticks)
        (1, 0.60, colorGREEN,  30),   # Normal — lasts 30 ticks
        (2, 0.30, colorBLUE,   20),   # Bonus  — lasts 20 ticks
        (3, 0.10, colorWHITE,  12),   # Rare   — lasts 12 ticks
    ]

    def __init__(self, snake_body):
        self.pos = Point(0, 0)
        self._pick_type()
        self.generate_random_pos(snake_body)

    def _pick_type(self):
        """Randomly choose food type based on weighted probability."""
        roll = random.random()
        cumulative = 0.0
        for value, prob, color, lifetime in self.FOOD_TYPES:
            cumulative += prob
            if roll < cumulative:
                self.value = value
                self.color = color
                self.lifetime = lifetime
                self.ticks_left = lifetime
                break

    def draw(self):
        # Draw food rectangle
        pygame.draw.rect(screen, self.color,
                         (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

        # Draw a small label with the food value inside the cell
        label_font = pygame.font.SysFont("Verdana", 16, bold=True)
        label = label_font.render(str(self.value), True, colorBLACK)
        label_rect = label.get_rect(
            center=(self.pos.x * CELL + CELL // 2,
                    self.pos.y * CELL + CELL // 2))
        screen.blit(label, label_rect)

        # Draw a shrinking timer bar at the bottom of the cell
        ratio = self.ticks_left / self.lifetime
        bar_w = int(CELL * ratio)
        bar_color = colorGREEN if ratio > 0.5 else colorYELLOW if ratio > 0.25 else colorRED
        pygame.draw.rect(screen, bar_color,
                         (self.pos.x * CELL, self.pos.y * CELL + CELL - 4,
                          bar_w, 4))

    def tick(self):
        """
        Called every game tick. Decrements the timer.
        Returns True if the food has expired and should be removed.
        """
        self.ticks_left -= 1
        return self.ticks_left <= 0

    def generate_random_pos(self, snake_body):
        """Place food at a random position that is not occupied by the snake."""
        while True:
            x = random.randint(0, WIDTH // CELL - 1)
            y = random.randint(0, HEIGHT // CELL - 1)

            on_snake = any(seg.x == x and seg.y == y for seg in snake_body)
            if not on_snake:
                self.pos.x = x
                self.pos.y = y
                break


clock = pygame.time.Clock()
snake = Snake()

# Start with a single food item on the board
food_list = [Food(snake.body)]

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

        # Check if snake ate any food
        eaten = snake.check_food_collision(food_list)
        if eaten:
            food_list.remove(eaten)
            food_list.append(Food(snake.body))   # spawn replacement

        # Tick every food's timer; remove expired ones and spawn replacements
        expired = [f for f in food_list if f.tick()]
        for f in expired:
            food_list.remove(f)
            food_list.append(Food(snake.body))   # spawn replacement for expired food

        # Game ends only if snake hits wall or itself
        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True

        snake.draw()
        for food in food_list:
            food.draw()

        # Display score and level in the top-left corner
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