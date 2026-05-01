import pygame
import random
import time

pygame.init()  # initializes all pygame modules

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

# Fonts
font_big = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
image_game_over = font_big.render("Game Over", True, colorBLACK)
image_game_over_rect = image_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2))

SPEED = 5
COINS = 0


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
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colorYELLOW, (15, 15), 15)
        pygame.draw.circle(self.image, colorBLACK, (15, 15), 15, 2)
        self.rect = self.image.get_rect()
        self.generate_random_rect()

    def generate_random_rect(self):
        # Coin appears randomly on the road
        self.rect.left = random.randint(20, WIDTH - self.rect.w - 20)
        self.rect.bottom = random.randint(-500, -50)

    def move(self):
        global SPEED
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
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
            SPEED += 0.2

    screen.blit(image_background, (0, 0))

    # Move and draw all sprites
    for entity in all_sprites:
        entity.move()
        screen.blit(entity.image, entity.rect)

    # If player collects coin, increase counter and move coin to a new place
    if pygame.sprite.spritecollideany(player, coin_sprites):
        COINS += 1
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
    screen.blit(coin_text, (WIDTH - 110, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
