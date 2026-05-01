import random
import pygame

from persistence import add_score, DIFFICULTY_CONFIG
from ui import BLACK, WHITE, GRAY, LIGHT_GRAY, GREEN, BLUE, RED, YELLOW, ORANGE, PURPLE, draw_text

WIDTH = 500
HEIGHT = 700
ROAD_LEFT = 70
ROAD_RIGHT = 430
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES
FINISH_DISTANCE = 5000
FPS = 60

COIN_TYPES = [
    (1, 0.60, YELLOW, 11),
    (2, 0.30, ORANGE, 14),
    (5, 0.10, PURPLE, 17),
]
POWER_TYPES = ["Nitro", "Shield", "Repair"]
POWER_COLORS = {"Nitro": ORANGE, "Shield": BLUE, "Repair": GREEN}


def lane_center(lane):
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2


def random_lane_x(width):
    lane = random.randint(0, LANES - 1)
    return lane_center(lane) - width // 2


class Player:
    def __init__(self, color):
        self.w = 42
        self.h = 72
        self.rect = pygame.Rect(WIDTH // 2 - self.w // 2, HEIGHT - 105, self.w, self.h)
        self.color = tuple(color)
        self.speed = 7
        self.shield = False
        self.crashes = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed // 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed // 2
        self.rect.left = max(ROAD_LEFT + 5, self.rect.left)
        self.rect.right = min(ROAD_RIGHT - 5, self.rect.right)
        self.rect.top = max(90, self.rect.top)
        self.rect.bottom = min(HEIGHT - 15, self.rect.bottom)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        pygame.draw.rect(screen, (190, 220, 255), (self.rect.x + 7, self.rect.y + 8, self.rect.w - 14, 18), border_radius=5)
        pygame.draw.circle(screen, BLACK, (self.rect.left + 8, self.rect.bottom - 10), 6)
        pygame.draw.circle(screen, BLACK, (self.rect.right - 8, self.rect.bottom - 10), 6)
        if self.shield:
            pygame.draw.ellipse(screen, BLUE, self.rect.inflate(16, 16), 3)


class FallingObject:
    def __init__(self, kind, speed, player_rect=None):
        self.kind = kind
        self.base_speed = speed
        self.timeout = 0
        if kind == "traffic":
            self.rect = pygame.Rect(random_lane_x(44), -90, 44, 74)
            self.color = random.choice([RED, ORANGE, PURPLE, (90, 90, 90)])
        elif kind in ["barrier", "pothole", "oil", "speed_bump", "nitro_strip"]:
            h = 26 if kind in ["barrier", "speed_bump", "nitro_strip"] else 38
            w = 72 if kind in ["barrier", "speed_bump", "nitro_strip"] else 42
            self.rect = pygame.Rect(random_lane_x(w), -80, w, h)
            self.color = {"barrier": RED, "pothole": BLACK, "oil": (25, 25, 25), "speed_bump": YELLOW, "nitro_strip": ORANGE}[kind]
        elif kind == "coin":
            value, _, color, radius = self.pick_coin_type()
            self.value = value
            self.color = color
            self.radius = radius
            self.rect = pygame.Rect(random_lane_x(radius * 2), -80, radius * 2 + 4, radius * 2 + 4)
        else:
            self.power_type = random.choice(POWER_TYPES)
            self.color = POWER_COLORS[self.power_type]
            self.rect = pygame.Rect(random_lane_x(34), -80, 34, 34)
            self.spawn_time = pygame.time.get_ticks()
            self.timeout = 8000

        if player_rect and self.rect.colliderect(player_rect.inflate(40, 260)):
            self.rect.y -= 260

    def pick_coin_type(self):
        roll = random.random()
        total = 0
        for item in COIN_TYPES:
            total += item[1]
            if roll <= total:
                return item
        return COIN_TYPES[0]

    def update(self, speed_multiplier=1.0):
        self.rect.y += self.base_speed * speed_multiplier

    def expired(self):
        if self.kind == "powerup":
            return pygame.time.get_ticks() - self.spawn_time > self.timeout
        return self.rect.top > HEIGHT + 20

    def draw(self, screen, font):
        if self.kind == "traffic":
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
            pygame.draw.rect(screen, (190, 220, 255), (self.rect.x + 7, self.rect.y + 7, self.rect.w - 14, 15), border_radius=4)
        elif self.kind == "coin":
            center = self.rect.center
            pygame.draw.circle(screen, self.color, center, self.radius)
            pygame.draw.circle(screen, BLACK, center, self.radius, 2)
            draw_text(screen, self.value, font, BLACK, center=center)
        elif self.kind == "powerup":
            pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
            draw_text(screen, self.power_type[0], font, WHITE, center=self.rect.center)
        elif self.kind == "oil":
            pygame.draw.ellipse(screen, self.color, self.rect)
            pygame.draw.ellipse(screen, GRAY, self.rect, 2)
        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, BLACK, self.rect)
            pygame.draw.ellipse(screen, GRAY, self.rect, 3)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
            label = "N" if self.kind == "nitro_strip" else "!"
            draw_text(screen, label, font, BLACK, center=self.rect.center)


class RacerGame:
    def __init__(self, screen, fonts, settings, username):
        self.screen = screen
        self.font_small = fonts["small"]
        self.font_medium = fonts["medium"]
        self.font_big = fonts["big"]
        self.settings = settings
        self.username = username or "Player"
        self.config = DIFFICULTY_CONFIG[settings["difficulty"]]
        self.player = Player(settings["car_color"])
        self.objects = []
        self.road_offset = 0
        self.score = 0
        self.coins = 0
        self.distance = 0.0
        self.game_over = False
        self.finished = False
        self.saved = False
        self.base_speed = self.config["speed"]
        self.active_power = None
        self.power_end_time = 0
        self.spawned_power = False
        self.traffic_timer = 0
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.event_timer = 0
        self.spawn_initial()

    def spawn_initial(self):
        for _ in range(2):
            self.objects.append(FallingObject("traffic", self.base_speed, self.player.rect))
        for _ in range(3):
            self.objects.append(FallingObject("coin", self.base_speed, self.player.rect))

    def difficulty_multiplier(self):
        return 1.0 + self.distance / 1700.0

    def current_speed_multiplier(self):
        multiplier = self.difficulty_multiplier()
        if self.active_power == "Nitro":
            multiplier += 0.65
        return multiplier

    def spawn_logic(self):
        density = self.config["density_scale"] * self.difficulty_multiplier()
        if random.random() < self.config["traffic_rate"] * density:
            self.objects.append(FallingObject("traffic", self.base_speed, self.player.rect))
        if random.random() < self.config["obstacle_rate"] * density:
            self.objects.append(FallingObject(random.choice(["barrier", "pothole", "oil"]), self.base_speed, self.player.rect))
        if random.random() < 0.018:
            self.objects.append(FallingObject("coin", self.base_speed, self.player.rect))
        if not any(o.kind == "powerup" for o in self.objects) and self.active_power is None and random.random() < 0.006:
            self.objects.append(FallingObject("powerup", self.base_speed, self.player.rect))
        if random.random() < 0.004:
            self.objects.append(FallingObject(random.choice(["speed_bump", "nitro_strip"]), self.base_speed, self.player.rect))

    def crash_or_shield(self):
        if self.player.shield:
            self.player.shield = False
            return False
        self.game_over = True
        return True

    def update_power(self):
        now = pygame.time.get_ticks()
        if self.active_power and now > self.power_end_time:
            self.active_power = None

    def update(self):
        if self.game_over:
            return
        self.update_power()
        self.player.update()
        self.spawn_logic()
        speed_multiplier = self.current_speed_multiplier()
        self.road_offset = (self.road_offset + self.base_speed * speed_multiplier) % 40
        self.distance += self.base_speed * speed_multiplier * 0.13
        self.score = self.coins * 25 + int(self.distance)
        if self.distance >= FINISH_DISTANCE:
            self.finished = True
            self.game_over = True
        for obj in self.objects:
            obj.update(speed_multiplier)
        self.handle_collisions()
        self.objects = [o for o in self.objects if not o.expired()]

    def handle_collisions(self):
        for obj in list(self.objects):
            if not self.player.rect.colliderect(obj.rect):
                continue
            if obj.kind == "coin":
                self.coins += obj.value
                self.score += obj.value * 25
                self.objects.remove(obj)
            elif obj.kind == "powerup":
                if obj.power_type == "Shield":
                    self.player.shield = True
                elif obj.power_type == "Repair":
                    if self.player.crashes > 0:
                        self.player.crashes -= 1
                    else:
                        self.objects = [o for o in self.objects if o.kind not in ["barrier", "pothole", "oil"] or o.rect.y < 0]
                else:
                    self.active_power = "Nitro"
                    self.power_end_time = pygame.time.get_ticks() + 4500
                self.objects.remove(obj)
            elif obj.kind == "nitro_strip":
                self.active_power = "Nitro"
                self.power_end_time = pygame.time.get_ticks() + 3000
                self.objects.remove(obj)
            elif obj.kind == "speed_bump":
                self.active_power = "Slow"
                self.power_end_time = pygame.time.get_ticks() + 2500
                self.objects.remove(obj)
            elif obj.kind in ["traffic", "barrier", "pothole", "oil"]:
                self.crash_or_shield()
                if not self.game_over and obj in self.objects:
                    self.objects.remove(obj)

    def save_result(self):
        if not self.saved:
            add_score(self.username, self.score, self.distance, self.coins, self.settings["difficulty"])
            self.saved = True

    def draw_road(self):
        self.screen.fill((35, 145, 70))
        pygame.draw.rect(self.screen, (60, 60, 60), (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_LEFT - 5, 0, 5, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_RIGHT, 0, 5, HEIGHT))
        for lane in range(1, LANES):
            x = ROAD_LEFT + lane * LANE_WIDTH
            for y in range(-40, HEIGHT, 80):
                pygame.draw.rect(self.screen, LIGHT_GRAY, (x - 2, y + self.road_offset, 4, 42))

    def draw_hud(self):
        pygame.draw.rect(self.screen, (240, 240, 240), (0, 0, WIDTH, 72))
        pygame.draw.line(self.screen, BLACK, (0, 72), (WIDTH, 72), 2)
        draw_text(self.screen, f"Player: {self.username}", self.font_small, BLACK, topleft=(10, 8))
        draw_text(self.screen, f"Score: {self.score}", self.font_small, BLACK, topleft=(10, 32))
        draw_text(self.screen, f"Coins: {self.coins}", self.font_small, BLACK, topleft=(140, 32))
        draw_text(self.screen, f"Distance: {int(self.distance)}/{FINISH_DISTANCE}", self.font_small, BLACK, topleft=(245, 8))
        draw_text(self.screen, f"Difficulty: {self.settings['difficulty']}", self.font_small, BLACK, topleft=(245, 32))
        power_text = "Shield" if self.player.shield else "None"
        if self.active_power:
            remaining = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
            power_text = f"{self.active_power} {remaining}s"
        draw_text(self.screen, f"Power: {power_text}", self.font_small, BLUE, topleft=(10, 54))

    def draw(self):
        self.draw_road()
        for obj in self.objects:
            obj.draw(self.screen, self.font_small)
        self.player.draw(self.screen)
        self.draw_hud()
