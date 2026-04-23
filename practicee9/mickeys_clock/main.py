import pygame
from clock import draw_clock

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey's Clock")

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_clock(screen, WIDTH, HEIGHT)

    pygame.display.flip()
    clock.tick(1)

pygame.quit()
