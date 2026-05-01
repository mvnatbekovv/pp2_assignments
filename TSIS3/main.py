import sys
import pygame

from persistence import load_settings, save_settings, load_leaderboard
from racer import RacerGame, WIDTH, HEIGHT, FPS
from ui import Button, draw_panel, draw_text, username_screen, WHITE, BLACK, DARK, BLUE, GREEN, RED, YELLOW, ORANGE, PURPLE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer")
clock = pygame.time.Clock()
fonts = {
    "small": pygame.font.SysFont("Verdana", 16),
    "medium": pygame.font.SysFont("Verdana", 24),
    "big": pygame.font.SysFont("Verdana", 48, bold=True),
}

settings = load_settings()
username = "Player"

COLOR_OPTIONS = [
    [40, 120, 255],
    [231, 76, 60],
    [46, 204, 113],
    [241, 196, 15],
    [155, 89, 182],
]
DIFFICULTIES = ["Easy", "Normal", "Hard"]


def draw_background(title):
    screen.fill((215, 235, 255))
    draw_text(screen, title, fonts["big"], DARK, center=(WIDTH // 2, 70))


def username_box(events):
    global username
    active = False
    rect = pygame.Rect(130, 122, 240, 38)
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            active = rect.collidepoint(event.pos)
        if active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            elif event.key == pygame.K_RETURN:
                active = False
            elif len(username) < 14 and event.unicode.strip():
                if username == "Player":
                    username = ""
                username += event.unicode
    pygame.draw.rect(screen, WHITE, rect, border_radius=8)
    pygame.draw.rect(screen, BLUE if active else BLACK, rect, 2, border_radius=8)
    draw_text(screen, username or "Enter name", fonts["medium"], BLACK, center=rect.center)
    draw_text(screen, "Username", fonts["small"], BLACK, center=(WIDTH // 2, 112))


def main_menu():
    global username
    buttons = [
        Button((150, 185, 200, 48), "Play", fonts["medium"]),
        Button((150, 250, 200, 48), "Leaderboard", fonts["medium"]),
        Button((150, 315, 200, 48), "Settings", fonts["medium"]),
        Button((150, 380, 200, 48), "Quit", fonts["medium"], color=RED),
    ]
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if buttons[0].clicked(event):
                username = username_screen(screen, clock, WIDTH, HEIGHT)
                return "play"
            if buttons[1].clicked(event):
                return "leaderboard"
            if buttons[2].clicked(event):
                return "settings"
            if buttons[3].clicked(event):
                pygame.quit(); sys.exit()
        draw_background("Racer")
        draw_panel(screen, (80, 120, 340, 360))
        draw_text(screen, "Click Play, enter name, press Enter", fonts["small"], BLACK, center=(WIDTH // 2, 145))
        draw_text(screen, f"Current player: {username}", fonts["small"], BLACK, center=(WIDTH // 2, 165))
        for button in buttons:
            button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def leaderboard_screen():
    back = Button((165, 620, 170, 45), "Back", fonts["medium"])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if back.clicked(event):
                return
        draw_background("Leaderboard Top 10")
        draw_panel(screen, (35, 110, 430, 480))
        draw_text(screen, "Rank   Name       Score    Distance", fonts["small"], BLACK, topleft=(60, 135))
        scores = load_leaderboard()
        if not scores:
            draw_text(screen, "No scores yet", fonts["medium"], BLACK, center=(WIDTH // 2, 330))
        for i, item in enumerate(scores[:10], start=1):
            y = 165 + (i - 1) * 38
            line = f"{i:<5} {item.get('name','Player')[:8]:<9} {item.get('score',0):<7} {item.get('distance',0)}m"
            draw_text(screen, line, fonts["small"], BLACK, topleft=(60, y))
        back.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def settings_screen():
    global settings
    save_back = Button((145, 610, 210, 45), "Save & Back", fonts["medium"], color=GREEN)
    sound_button = Button((145, 170, 210, 45), "", fonts["medium"])
    difficulty_button = Button((145, 260, 210, 45), "", fonts["medium"], color=PURPLE)
    color_rects = [pygame.Rect(90 + i * 65, 385, 46, 46) for i in range(len(COLOR_OPTIONS))]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]
            if difficulty_button.clicked(event):
                idx = DIFFICULTIES.index(settings["difficulty"])
                settings["difficulty"] = DIFFICULTIES[(idx + 1) % len(DIFFICULTIES)]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, color in zip(color_rects, COLOR_OPTIONS):
                    if rect.collidepoint(event.pos):
                        settings["car_color"] = color
            if save_back.clicked(event):
                save_settings(settings)
                return
        draw_background("Settings")
        draw_panel(screen, (55, 120, 390, 430))
        sound_button.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"
        sound_button.draw(screen)
        difficulty_button.draw(screen)
        draw_text(screen, "Car color", fonts["medium"], BLACK, center=(WIDTH // 2, 350))
        for rect, color in zip(color_rects, COLOR_OPTIONS):
            pygame.draw.rect(screen, color, rect, border_radius=8)
            border = 5 if settings["car_color"] == color else 2
            pygame.draw.rect(screen, BLACK, rect, border, border_radius=8)
        draw_text(screen, "Settings are saved to settings.json", fonts["small"], BLACK, center=(WIDTH // 2, 510))
        save_back.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(game):
    game.save_result()
    retry = Button((150, 390, 200, 48), "Retry", fonts["medium"], color=GREEN)
    menu = Button((150, 455, 200, 48), "Main Menu", fonts["medium"])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"
        screen.fill((235, 235, 235))
        title = "Finished!" if game.finished else "Game Over"
        draw_text(screen, title, fonts["big"], RED if not game.finished else GREEN, center=(WIDTH // 2, 120))
        draw_panel(screen, (75, 180, 350, 175))
        draw_text(screen, f"Score: {game.score}", fonts["medium"], BLACK, center=(WIDTH // 2, 220))
        draw_text(screen, f"Distance: {int(game.distance)}", fonts["medium"], BLACK, center=(WIDTH // 2, 260))
        draw_text(screen, f"Coins: {game.coins}", fonts["medium"], BLACK, center=(WIDTH // 2, 300))
        retry.draw(screen)
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def play_game():
    while True:
        game = RacerGame(screen, fonts, settings, username)
        while not game.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game.game_over = True
            game.update()
            game.draw()
            pygame.display.flip()
            clock.tick(FPS)
        result = game_over_screen(game)
        if result != "retry":
            return


def main():
    while True:
        action = main_menu()
        if action == "play":
            play_game()
        elif action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings_screen()


if __name__ == "__main__":
    main()
