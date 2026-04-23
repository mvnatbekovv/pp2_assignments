import pygame


def draw_ball(screen, x, y, radius):
    pygame.draw.circle(screen, (255, 0, 0), (x, y), radius)
