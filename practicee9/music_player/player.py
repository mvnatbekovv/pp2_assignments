import pygame


start_ticks = 0


def play_music(playlist, current_track):
    global start_ticks
    pygame.mixer.music.load(playlist[current_track])
    pygame.mixer.music.play()
    start_ticks = pygame.time.get_ticks()


def stop_music():
    pygame.mixer.music.stop()


def next_music(playlist, current_track):
    current_track += 1
    if current_track >= len(playlist):
        current_track = 0

    play_music(playlist, current_track)
    return current_track


def previous_music(playlist, current_track):
    current_track -= 1
    if current_track < 0:
        current_track = len(playlist) - 1

    play_music(playlist, current_track)
    return current_track


def draw_player(screen, font_big, font_small, playlist, current_track, is_playing):
    screen.fill((255, 255, 255))

    title = font_big.render("Music Player", True, (0, 0, 0))
    track = font_small.render("Current track: " + playlist[current_track], True, (0, 0, 255))

    if is_playing:
        status = font_small.render("Status: Playing", True, (0, 150, 0))
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    else:
        status = font_small.render("Status: Stopped", True, (255, 0, 0))
        seconds = 0

    progress = font_small.render("Track position: " + str(seconds) + " sec", True, (0, 0, 0))
    controls1 = font_small.render("P - Play    S - Stop", True, (0, 0, 0))
    controls2 = font_small.render("N - Next    B - Previous    Q - Quit", True, (0, 0, 0))

    screen.blit(title, (230, 60))
    screen.blit(track, (140, 170))
    screen.blit(status, (140, 220))
    screen.blit(progress, (140, 270))
    screen.blit(controls1, (180, 360))
    screen.blit(controls2, (120, 400))
