import pygame
import random
import time

pygame.init()  # Initializes all pygame modules

WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

# Images from lecture/CodersLegacy racer example
image_background = pygame.image.load('resources/AnimatedStreet.png')
image_player = pygame.image.load('resources/Player.png')
image_enemy = pygame.image.load('resources/Enemy.png')

# Background music and crash sound
pygame.mixer.music.load('resources/background.wav')
pygame.mixer.music.play(-1)
sound_crash = pygame.mixer.Sound('resources/crash.wav')

# Colors
colorBLACK = (0, 0, 0)
colorRED = (255, 0, 0)
colorYELLOW = (255, 255, 0)
colorORANGE = (255, 140, 0)
colorCYAN = (0, 220, 255)
colorWHITE = (255, 255, 255)

# Fonts
font_big = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
image_game_over = font_big.render("Game Over", True, colorBLACK)
image_game_over_rect = image_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2))

SPEED = 5
COINS = 0

# Every N coins the enemy speeds up
SPEED_UP_EVERY = 5


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT
        self.speed = 5

    def move(self):
        # Player can move only left and right
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)

        # Do not let the player leave the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_enemy
        self.rect = self.image.get_rect()
        self.generate_random_rect()

    def generate_random_rect(self):
        # Enemy appears at a random x-position from the top
        self.rect.left = random.randint(0, WIDTH - self.rect.w)
        self.rect.bottom = 0

    def move(self):
        global SPEED
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            self.generate_random_rect()


class Coin(pygame.sprite.Sprite):
    """
    Coin with a random weight/value.
    Weights and their probabilities:
      - Bronze (1 pt):  60% chance — small yellow circle
      - Silver (2 pt):  30% chance — larger orange circle
      - Gold   (5 pt):  10% chance — large cyan circle
    """

    # (value, probability, color, radius) tuples
    COIN_TYPES = [
        (1, 0.60, colorYELLOW,  10),   # Bronze
        (2, 0.30, colorORANGE,  14),   # Silver
        (5, 0.10, colorCYAN,    18),   # Gold
    ]

    def __init__(self):
        super().__init__()
        self._pick_type()
        self.generate_random_rect()

    def _pick_type(self):
        """Choose coin type based on weighted probability."""
        roll = random.random()
        cumulative = 0.0
        for value, prob, color, radius in self.COIN_TYPES:
            cumulative += prob
            if roll < cumulative:
                self.value = value
                self.color = color
                self.radius = radius
                break

        # Create surface sized to the coin
        size = self.radius * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        pygame.draw.circle(self.image, self.color, (cx, cy), self.radius)
        pygame.draw.circle(self.image, colorBLACK, (cx, cy), self.radius, 2)

        # Draw value label inside the coin
        label_font = pygame.font.SysFont("Verdana", max(10, self.radius - 2), bold=True)
        label = label_font.render(str(self.value), True, colorBLACK)
        label_rect = label.get_rect(center=(cx, cy))
        self.image.blit(label, label_rect)

        self.rect = self.image.get_rect()

    def generate_random_rect(self):
        # Coin appears randomly on the road, above the visible area
        self.rect.left = random.randint(20, WIDTH - self.rect.w - 20)
        self.rect.bottom = random.randint(-500, -50)

    def move(self):
        global SPEED
        self.rect.move_ip(0, SPEED)
        # When coin leaves the screen, respawn it with a new random type
        if self.rect.top > HEIGHT:
            self._pick_type()           # re-roll coin type on each respawn
            self.generate_random_rect()


clock = pygame.time.Clock()
FPS = 60

player = Player()
enemy = Enemy()
coin = Coin()

all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
coin_sprites = pygame.sprite.Group()

all_sprites.add(player, enemy, coin)
enemy_sprites.add(enemy)
coin_sprites.add(coin)

# User event from CodersLegacy tutorial: increases game speed over time
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == INC_SPEED:
            # Gradually increase background scroll speed
            SPEED += 0.2

    screen.blit(image_background, (0, 0))

    # Move and draw all sprites
    for entity in all_sprites:
        entity.move()
        screen.blit(entity.image, entity.rect)

    # If player collects coin, add its value and possibly speed up enemy
    if pygame.sprite.spritecollideany(player, coin_sprites):
        prev_milestone = COINS // SPEED_UP_EVERY
        COINS += coin.value
        new_milestone = COINS // SPEED_UP_EVERY

        # Every SPEED_UP_EVERY coins the enemy gets a noticeable speed boost
        if new_milestone > prev_milestone:
            SPEED += 1.0

        # Respawn coin with a new random type after collection
        coin._pick_type()
        coin.generate_random_rect()

    # If player collides with enemy, game ends
    if pygame.sprite.spritecollideany(player, enemy_sprites):
        sound_crash.play()
        time.sleep(0.5)
        running = False
        screen.fill(colorRED)
        screen.blit(image_game_over, image_game_over_rect)
        pygame.display.flip()
        time.sleep(2)

    # Show number of collected coins in the top right corner
    coin_text = font_small.render("Coins: " + str(COINS), True, colorBLACK)
    screen.blit(coin_text, (WIDTH - 120, 10))

    # Show next speed-up threshold
    next_up = SPEED_UP_EVERY - (COINS % SPEED_UP_EVERY)
    next_text = font_small.render(f"Next boost: {next_up}", True, colorBLACK)
    screen.blit(next_text, (WIDTH - 150, 35))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()