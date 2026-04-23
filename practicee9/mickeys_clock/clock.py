import pygame
import datetime


clock_face = pygame.image.load("images/clock_face.png")
right_hand = pygame.image.load("images/right_hand.png")
left_hand = pygame.image.load("images/left_hand.png")


def draw_clock(screen, width, height):
    now = datetime.datetime.now()

    minutes = now.minute
    seconds = now.second

    minute_angle = -minutes * 6
    second_angle = -seconds * 6

    screen.fill((255, 255, 255))

    face = pygame.transform.scale(clock_face, (500, 500))
    face_rect = face.get_rect(center=(width // 2, height // 2))
    screen.blit(face, face_rect)

    minute_hand = pygame.transform.rotate(right_hand, minute_angle)
    minute_rect = minute_hand.get_rect(center=(width // 2, height // 2))
    screen.blit(minute_hand, minute_rect)

    second_hand = pygame.transform.rotate(left_hand, second_angle)
    second_rect = second_hand.get_rect(center=(width // 2, height // 2))
    screen.blit(second_hand, second_rect)
