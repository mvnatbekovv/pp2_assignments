import pygame
from player import draw_player, play_music, stop_music, next_music, previous_music

pygame.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font_big = pygame.font.SysFont("comicsansms", 48)
font_small = pygame.font.SysFont("comicsansms", 28)

clock = pygame.time.Clock()

playlist = [
    "music/track1.wav",
    "music/track2.wav"
]

current_track = 0
is_playing = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                is_playing = True
                play_music(playlist, current_track)
            if event.key == pygame.K_s:
                is_playing = False
                stop_music()
            if event.key == pygame.K_n:
                current_track = next_music(playlist, current_track)
                is_playing = True
            if event.key == pygame.K_b:
                current_track = previous_music(playlist, current_track)
                is_playing = True
            if event.key == pygame.K_q:
                running = False

    draw_player(screen, font_big, font_small, playlist, current_track, is_playing)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
