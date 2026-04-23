import pygame
from ball import draw_ball

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

x = WIDTH // 2
y = HEIGHT // 2
radius = 25
step = 20

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if y - step - radius >= 0:
                    y -= step
            if event.key == pygame.K_DOWN:
                if y + step + radius <= HEIGHT:
                    y += step
            if event.key == pygame.K_LEFT:
                if x - step - radius >= 0:
                    x -= step
            if event.key == pygame.K_RIGHT:
                if x + step + radius <= WIDTH:
                    x += step

    screen.fill((255, 255, 255))
    draw_ball(screen, x, y, radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
