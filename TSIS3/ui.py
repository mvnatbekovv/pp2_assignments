import pygame

WHITE = (245, 245, 245)
BLACK = (18, 18, 18)
DARK = (34, 39, 46)
GRAY = (110, 110, 110)
LIGHT_GRAY = (220, 220, 220)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
YELLOW = (241, 196, 15)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)


def draw_text(surface, text, font, color, center=None, topleft=None):
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = center
    if topleft:
        rect.topleft = topleft
    surface.blit(image, rect)
    return rect


class Button:
    def __init__(self, rect, text, font, color=BLUE, hover_color=GREEN, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        draw_text(surface, self.text, self.font, self.text_color, center=self.rect.center)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_panel(surface, rect, color=(250, 250, 250)):
    pygame.draw.rect(surface, color, rect, border_radius=16)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=16)


def username_screen(screen, clock, width, height):
    username = ""
    font = pygame.font.SysFont("Verdana", 24)
    hint_font = pygame.font.SysFont("Verdana", 18)
    title_font = pygame.font.SysFont("Verdana", 32, bold=True)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                if event.key == pygame.K_ESCAPE:
                    return "Player"
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 12 and event.unicode and event.unicode.isprintable():
                    username += event.unicode

        screen.fill(DARK)
        title = title_font.render("Enter username", True, WHITE)
        screen.blit(title, title.get_rect(center=(width // 2, 180)))

        input_rect = pygame.Rect(80, 260, width - 160, 50)
        pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=8)
        input_text = font.render(username, True, WHITE)
        screen.blit(input_text, (95, 270))

        hint = hint_font.render("Press ENTER to start", True, YELLOW)
        screen.blit(hint, hint.get_rect(center=(width // 2, 350)))
        pygame.display.flip()
