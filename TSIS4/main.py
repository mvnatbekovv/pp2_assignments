import random
import sys
import pygame

from settings import load_settings, save_settings

try:
    import db
except Exception:
    db = None

pygame.init()

WIDTH, HEIGHT = 720, 720
CELL = 24
GRID_W, GRID_H = WIDTH // CELL, HEIGHT // CELL
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake")
CLOCK = pygame.time.Clock()

BLACK = (12, 12, 16)
WHITE = (245, 245, 245)
GRAY = (70, 70, 80)
DARK_GRAY = (35, 35, 45)
GREEN = (0, 190, 90)
BLUE = (40, 120, 255)
RED = (220, 45, 45)
DARK_RED = (120, 0, 0)
YELLOW = (255, 215, 0)
PURPLE = (160, 80, 255)
ORANGE = (255, 150, 40)
CYAN = (70, 220, 230)

FONT_SMALL = pygame.font.SysFont("Verdana", 16)
FONT = pygame.font.SysFont("Verdana", 22)
FONT_BIG = pygame.font.SysFont("Verdana", 42, bold=True)

settings = load_settings()
username = "Player"
db_ready = False
last_db_error = ""


def draw_text(text, font, color, center=None, topleft=None):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect()
    if center:
        rect.center = center
    if topleft:
        rect.topleft = topleft
    SCREEN.blit(surface, rect)
    return rect


class Button:
    def __init__(self, x, y, w, h, text, color=BLUE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = tuple(min(255, c + 30) for c in self.color) if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(SCREEN, color, self.rect, border_radius=10)
        pygame.draw.rect(SCREEN, WHITE, self.rect, 2, border_radius=10)
        draw_text(self.text, FONT, WHITE, center=self.rect.center)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def setup_database():
    global db_ready, last_db_error
    if db is None:
        last_db_error = "psycopg2 is not installed"
        db_ready = False
        return False
    try:
        db.init_db()
        db_ready = True
        last_db_error = ""
        return True
    except Exception as exc:
        db_ready = False
        last_db_error = str(exc).split("\n")[0]
        return False


def personal_best(name):
    if not db_ready:
        return 0
    try:
        return db.get_personal_best(name)
    except Exception:
        return 0


def save_score(name, score, level):
    if not db_ready:
        return
    try:
        db.save_result(name, score, level)
    except Exception:
        pass


def fetch_leaderboard():
    if not db_ready:
        return []
    try:
        return db.get_leaderboard(10)
    except Exception:
        return []


def random_empty_cell(snake, foods=None, poison=None, powerup=None, obstacles=None):
    foods = foods or []
    obstacles = obstacles or set()
    busy = set(snake)
    busy.update(obstacles)
    for f in foods:
        busy.add(f["pos"])
    if poison:
        busy.add(poison["pos"])
    if powerup:
        busy.add(powerup["pos"])
    for _ in range(500):
        pos = (random.randint(1, GRID_W - 2), random.randint(1, GRID_H - 2))
        if pos not in busy:
            return pos
    return (1, 1)


def create_food(snake, foods, obstacles):
    roll = random.random()
    if roll < 0.60:
        value, color, lifetime = 1, GREEN, 9000
    elif roll < 0.90:
        value, color, lifetime = 2, BLUE, 7000
    else:
        value, color, lifetime = 3, WHITE, 5000
    return {
        "pos": random_empty_cell(snake, foods=foods, obstacles=obstacles),
        "value": value,
        "color": color,
        "created": pygame.time.get_ticks(),
        "lifetime": lifetime,
    }


def create_poison(snake, foods, obstacles):
    return {
        "pos": random_empty_cell(snake, foods=foods, obstacles=obstacles),
        "created": pygame.time.get_ticks(),
        "lifetime": 10000,
    }


def create_powerup(snake, foods, poison, obstacles):
    kind = random.choice(["boost", "slow", "shield"])
    colors = {"boost": ORANGE, "slow": CYAN, "shield": PURPLE}
    return {
        "kind": kind,
        "pos": random_empty_cell(snake, foods=foods, poison=poison, obstacles=obstacles),
        "color": colors[kind],
        "created": pygame.time.get_ticks(),
        "lifetime": 8000,
    }


def create_obstacles(level, snake, foods):
    if level < 3:
        return set()
    obstacles = set()
    amount = min(6 + level * 2, 35)
    protected = set(snake)
    head = snake[0]
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
        protected.add((head[0] + dx, head[1] + dy))
    while len(obstacles) < amount:
        pos = (random.randint(2, GRID_W - 3), random.randint(2, GRID_H - 3))
        if pos in protected:
            continue
        if any(f["pos"] == pos for f in foods):
            continue
        obstacles.add(pos)
    return obstacles


def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(SCREEN, DARK_GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(SCREEN, DARK_GRAY, (0, y), (WIDTH, y))


def username_screen():
    global username
    text = username if username != "Player" else ""
    while True:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text.strip():
                    username = text.strip()[:50]
                    return
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 18 and event.unicode and event.unicode.isprintable():
                    text += event.unicode

        SCREEN.fill(BLACK)
        draw_text("Enter username", FONT_BIG, WHITE, center=(WIDTH // 2, 210))
        box = pygame.Rect(190, 310, 340, 55)
        pygame.draw.rect(SCREEN, WHITE, box, 2, border_radius=8)
        draw_text(text or "Your name", FONT, WHITE, center=box.center)
        draw_text("Press ENTER to start", FONT_SMALL, YELLOW, center=(WIDTH // 2, 395))
        pygame.display.flip()


def main_menu():
    buttons = [
        Button(260, 260, 200, 50, "Play", GREEN),
        Button(260, 325, 200, 50, "Leaderboard", BLUE),
        Button(260, 390, 200, 50, "Settings", PURPLE),
        Button(260, 455, 200, 50, "Quit", RED),
    ]
    while True:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if buttons[0].clicked(event):
                username_screen()
                game_loop()
            if buttons[1].clicked(event):
                leaderboard_screen()
            if buttons[2].clicked(event):
                settings_screen()
            if buttons[3].clicked(event):
                pygame.quit(); sys.exit()

        SCREEN.fill(BLACK)
        draw_text("TSIS4 Snake", FONT_BIG, GREEN, center=(WIDTH // 2, 145))
        draw_text(f"Player: {username}", FONT, WHITE, center=(WIDTH // 2, 205))
        for button in buttons:
            button.draw()
        if db_ready:
            draw_text("Database: connected", FONT_SMALL, GREEN, center=(WIDTH // 2, 535))
        else:
            draw_text("Database is not connected. Edit config.py and create DB snake.", FONT_SMALL, YELLOW, center=(WIDTH // 2, 535))
            if last_db_error:
                draw_text(last_db_error[:70], FONT_SMALL, RED, center=(WIDTH // 2, 560))
        pygame.display.flip()


def leaderboard_screen():
    back = Button(260, 625, 200, 45, "Back", BLUE)
    while True:
        CLOCK.tick(60)
        rows = fetch_leaderboard()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if back.clicked(event):
                return
        SCREEN.fill(BLACK)
        draw_text("Leaderboard Top 10", FONT_BIG, WHITE, center=(WIDTH // 2, 70))
        draw_text("Rank   Username              Score   Level   Date", FONT_SMALL, YELLOW, topleft=(90, 135))
        y = 175
        if not rows:
            draw_text("No scores yet or database is not connected.", FONT, RED, center=(WIDTH // 2, 300))
        for i, row in enumerate(rows, 1):
            name, score, level, played_at = row
            date = played_at.strftime("%Y-%m-%d") if hasattr(played_at, "strftime") else str(played_at)[:10]
            line = f"{i:<5} {name:<20} {score:<7} {level:<7} {date}"
            draw_text(line, FONT_SMALL, WHITE, topleft=(90, y))
            y += 36
        back.draw()
        pygame.display.flip()


def settings_screen():
    global settings
    colors = [[255, 220, 0], [0, 220, 100], [50, 150, 255], [255, 90, 90]]
    grid_btn = Button(230, 210, 260, 45, "Toggle grid", BLUE)
    sound_btn = Button(230, 275, 260, 45, "Toggle sound", BLUE)
    color_btn = Button(230, 340, 260, 45, "Change snake color", PURPLE)
    save_btn = Button(230, 450, 260, 45, "Save & Back", GREEN)
    while True:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if grid_btn.clicked(event):
                settings["grid"] = not settings.get("grid", True)
            if sound_btn.clicked(event):
                settings["sound"] = not settings.get("sound", True)
            if color_btn.clicked(event):
                current = settings.get("snake_color", colors[0])
                idx = colors.index(current) if current in colors else 0
                settings["snake_color"] = colors[(idx + 1) % len(colors)]
            if save_btn.clicked(event):
                save_settings(settings)
                return
        SCREEN.fill(BLACK)
        draw_text("Settings", FONT_BIG, WHITE, center=(WIDTH // 2, 110))
        grid_btn.draw(); sound_btn.draw(); color_btn.draw(); save_btn.draw()
        draw_text(f"Grid: {'ON' if settings.get('grid', True) else 'OFF'}", FONT_SMALL, WHITE, center=(WIDTH // 2, 260))
        draw_text(f"Sound: {'ON' if settings.get('sound', True) else 'OFF'}", FONT_SMALL, WHITE, center=(WIDTH // 2, 325))
        pygame.draw.rect(SCREEN, tuple(settings.get("snake_color", [255, 220, 0])), (330, 395, 60, 30), border_radius=6)
        draw_text("Snake color", FONT_SMALL, WHITE, center=(WIDTH // 2, 420))
        pygame.display.flip()


def draw_game(snake, foods, poison, powerup, obstacles, score, level, best, active_power, power_end, shield):
    SCREEN.fill(BLACK)
    if settings.get("grid", True):
        draw_grid()
    for ox, oy in obstacles:
        pygame.draw.rect(SCREEN, GRAY, (ox * CELL, oy * CELL, CELL, CELL))
    for food in foods:
        x, y = food["pos"]
        pygame.draw.rect(SCREEN, food["color"], (x * CELL, y * CELL, CELL, CELL), border_radius=5)
        draw_text(food["value"], FONT_SMALL, BLACK, center=(x * CELL + CELL // 2, y * CELL + CELL // 2))
    if poison:
        x, y = poison["pos"]
        pygame.draw.rect(SCREEN, DARK_RED, (x * CELL, y * CELL, CELL, CELL), border_radius=5)
        draw_text("P", FONT_SMALL, WHITE, center=(x * CELL + CELL // 2, y * CELL + CELL // 2))
    if powerup:
        x, y = powerup["pos"]
        pygame.draw.rect(SCREEN, powerup["color"], (x * CELL, y * CELL, CELL, CELL), border_radius=5)
        label = {"boost": "B", "slow": "S", "shield": "H"}[powerup["kind"]]
        draw_text(label, FONT_SMALL, BLACK, center=(x * CELL + CELL // 2, y * CELL + CELL // 2))

    snake_color = tuple(settings.get("snake_color", [255, 220, 0]))
    for i, (x, y) in enumerate(snake):
        color = GREEN if i == 0 else snake_color
        pygame.draw.rect(SCREEN, color, (x * CELL, y * CELL, CELL, CELL), border_radius=5)

    hud = f"Score: {score}   Level: {level}   Best: {best}   Length: {len(snake)}"
    draw_text(hud, FONT_SMALL, WHITE, topleft=(10, 8))
    if active_power:
        left = max(0, (power_end - pygame.time.get_ticks()) // 1000)
        draw_text(f"Power: {active_power} {left}s", FONT_SMALL, YELLOW, topleft=(10, 34))
    if shield:
        draw_text("Shield ready", FONT_SMALL, PURPLE, topleft=(10, 58))


def game_over_screen(score, level, best):
    retry = Button(250, 390, 220, 48, "Retry", GREEN)
    menu = Button(250, 455, 220, 48, "Main Menu", BLUE)
    while True:
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if retry.clicked(event):
                game_loop(); return
            if menu.clicked(event):
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop(); return
                if event.key == pygame.K_ESCAPE:
                    return
        SCREEN.fill(BLACK)
        draw_text("Game Over", FONT_BIG, RED, center=(WIDTH // 2, 180))
        draw_text(f"Final score: {score}", FONT, WHITE, center=(WIDTH // 2, 255))
        draw_text(f"Level reached: {level}", FONT, WHITE, center=(WIDTH // 2, 290))
        draw_text(f"Personal best: {max(best, score)}", FONT, YELLOW, center=(WIDTH // 2, 325))
        retry.draw(); menu.draw()
        pygame.display.flip()


def game_loop():
    score = 0
    level = 1
    foods_eaten = 0
    base_fps = 8
    snake = [(GRID_W // 2, GRID_H // 2), (GRID_W // 2 - 1, GRID_H // 2), (GRID_W // 2 - 2, GRID_H // 2)]
    direction = (1, 0)
    next_direction = direction
    foods = []
    obstacles = set()
    for _ in range(2):
        foods.append(create_food(snake, foods, obstacles))
    poison = create_poison(snake, foods, obstacles)
    powerup = None
    next_power_spawn = pygame.time.get_ticks() + 6000
    active_power = None
    power_end = 0
    shield = False
    best = personal_best(username)
    saved = False

    while True:
        now = pygame.time.get_ticks()
        fps = base_fps + (level - 1) * 2
        if active_power == "boost":
            fps += 5
        if active_power == "slow":
            fps = max(4, fps - 4)
        CLOCK.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    next_direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    return

        if active_power and now >= power_end:
            active_power = None

        direction = next_direction
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        hit_wall = new_head[0] < 0 or new_head[0] >= GRID_W or new_head[1] < 0 or new_head[1] >= GRID_H
        hit_self = new_head in snake
        hit_obstacle = new_head in obstacles
        collision = hit_wall or hit_self or hit_obstacle

        if collision:
            if shield:
                shield = False
                new_head = head
            else:
                if not saved:
                    save_score(username, score, level)
                    saved = True
                game_over_screen(score, level, best)
                return

        snake.insert(0, new_head)
        grow = False

        for food in foods[:]:
            if new_head == food["pos"]:
                score += food["value"]
                foods_eaten += 1
                grow = True
                foods.remove(food)
                foods.append(create_food(snake, foods, obstacles))
                if foods_eaten % 3 == 0:
                    level += 1
                    obstacles = create_obstacles(level, snake, foods)

        if poison and new_head == poison["pos"]:
            for _ in range(2):
                if len(snake) > 1:
                    snake.pop()
            poison = create_poison(snake, foods, obstacles)
            if len(snake) <= 1:
                if not saved:
                    save_score(username, score, level)
                    saved = True
                game_over_screen(score, level, best)
                return

        if powerup and new_head == powerup["pos"]:
            if powerup["kind"] == "shield":
                shield = True
            else:
                active_power = powerup["kind"]
                power_end = now + 5000
            powerup = None
            next_power_spawn = now + random.randint(7000, 12000)

        if not grow:
            snake.pop()

        for food in foods[:]:
            if now - food["created"] > food["lifetime"]:
                foods.remove(food)
                foods.append(create_food(snake, foods, obstacles))
        if poison and now - poison["created"] > poison["lifetime"]:
            poison = create_poison(snake, foods, obstacles)
        if powerup and now - powerup["created"] > powerup["lifetime"]:
            powerup = None
            next_power_spawn = now + random.randint(6000, 10000)
        if powerup is None and now >= next_power_spawn:
            powerup = create_powerup(snake, foods, poison, obstacles)

        draw_game(snake, foods, poison, powerup, obstacles, score, level, best, active_power, power_end, shield)
        pygame.display.flip()


if __name__ == "__main__":
    setup_database()
    main_menu()
