import os
import sys
from datetime import datetime

import pygame

from tools import SHAPE_DRAWERS, flood_fill

pygame.init()

WIDTH, HEIGHT = 1000, 700
PANEL_H = 92
CANVAS_H = HEIGHT - PANEL_H
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (225, 225, 225)
DARK_GRAY = (90, 90, 90)
GREEN = (90, 200, 120)
YELLOW = (255, 240, 120)

COLORS = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 180, 0),
    (0, 0, 255), (255, 165, 0), (255, 255, 0), (128, 0, 128),
    (0, 255, 255), (255, 20, 147), (139, 69, 19), (128, 128, 128),
]

TOOLS = [
    "pencil", "line", "eraser", "fill", "text",
    "rect", "square", "circle", "rtriangle", "eqtriangle", "rhombus",
]

TOOL_LABELS = {
    "pencil": "Pencil",
    "line": "Line",
    "eraser": "Eraser",
    "fill": "Fill",
    "text": "Text",
    "rect": "Rect",
    "square": "Square",
    "circle": "Circle",
    "rtriangle": "RTri",
    "eqtriangle": "EqTri",
    "rhombus": "Rhombus",
}

BRUSH_SIZES = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}
SHAPE_TOOLS = set(SHAPE_DRAWERS.keys())

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 15)
small_font = pygame.font.SysFont("Arial", 13)
text_font = pygame.font.SysFont("Arial", 28)


def save_canvas(canvas: pygame.Surface) -> str:
    os.makedirs("saves", exist_ok=True)
    filename = datetime.now().strftime("saves/paint_%Y%m%d_%H%M%S.png")
    pygame.image.save(canvas, filename)
    return filename


def canvas_pos(mouse_pos):
    mx, my = mouse_pos
    return mx, my - PANEL_H


def on_canvas(mouse_pos) -> bool:
    return mouse_pos[1] >= PANEL_H


def make_tool_buttons():
    buttons = {}
    start_x = 485
    start_y = 6
    button_w = 78
    button_h = 25
    gap = 5

    for i, tool in enumerate(TOOLS):
        row = i // 6
        col = i % 6
        rect = pygame.Rect(start_x + col * (button_w + gap), start_y + row * (button_h + gap), button_w, button_h)
        buttons[tool] = rect
    return buttons


TOOL_BUTTONS = make_tool_buttons()
SIZE_BUTTONS = {
    2: pygame.Rect(195, 53, 58, 28),
    5: pygame.Rect(260, 53, 58, 28),
    10: pygame.Rect(325, 53, 58, 28),
}


def draw_panel(current_color, current_tool, brush_size, status_message):
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(screen, DARK_GRAY, (0, PANEL_H - 1), (WIDTH, PANEL_H - 1), 2)

    for i, color in enumerate(COLORS):
        rect = pygame.Rect(10 + i * 37, 8, 30, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        if color == current_color:
            pygame.draw.rect(screen, YELLOW, rect.inflate(5, 5), 3)

    info = font.render("Keys: 1=small  2=medium  3=large  Ctrl+S=save  Enter=confirm text  Esc=cancel text", True, BLACK)
    screen.blit(info, (10, 42))

    for size, rect in SIZE_BUTTONS.items():
        color = GREEN if brush_size == size else (190, 190, 190)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)
        label = small_font.render(f"{size}px", True, BLACK)
        screen.blit(label, (rect.x + 13, rect.y + 7))

    for tool, rect in TOOL_BUTTONS.items():
        color = GREEN if tool == current_tool else (190, 190, 190)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)
        label = small_font.render(TOOL_LABELS[tool], True, BLACK)
        screen.blit(label, (rect.x + 6, rect.y + 6))

    if status_message:
        status = small_font.render(status_message, True, (40, 70, 160))
        screen.blit(status, (485, 68))


def draw_text_preview(text_value, text_pos):
    if text_pos is None:
        return
    rendered = text_font.render(text_value + "|", True, BLACK)
    screen.blit(rendered, (text_pos[0], text_pos[1] + PANEL_H))


def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(WHITE)

    current_color = BLACK
    current_tool = "pencil"
    brush_size = 5

    drawing = False
    start_pos = None
    last_pos = None

    text_mode = False
    text_pos = None
    text_value = ""
    status_message = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    if event.key == pygame.K_s:
                        status_message = f"Saved: {save_canvas(canvas)}"
                        continue

                if text_mode:
                    if event.key == pygame.K_RETURN:
                        if text_value.strip():
                            rendered = text_font.render(text_value, True, current_color)
                            canvas.blit(rendered, text_pos)
                        text_mode = False
                        text_pos = None
                        text_value = ""
                        current_tool = "text"
                        continue
                    if event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_pos = None
                        text_value = ""
                        status_message = "Text cancelled"
                        continue
                    if event.key == pygame.K_BACKSPACE:
                        text_value = text_value[:-1]
                        continue
                    if event.unicode:
                        text_value += event.unicode
                        continue

                if event.key in BRUSH_SIZES:
                    brush_size = BRUSH_SIZES[event.key]
                    status_message = f"Brush size: {brush_size}px"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if my < PANEL_H:
                    for i, color in enumerate(COLORS):
                        rect = pygame.Rect(10 + i * 37, 8, 30, 30)
                        if rect.collidepoint(mx, my):
                            current_color = color

                    for size, rect in SIZE_BUTTONS.items():
                        if rect.collidepoint(mx, my):
                            brush_size = size
                            status_message = f"Brush size: {brush_size}px"

                    for tool, rect in TOOL_BUTTONS.items():
                        if rect.collidepoint(mx, my):
                            current_tool = tool
                            text_mode = False
                            text_value = ""
                    continue

                pos = canvas_pos(event.pos)

                if current_tool == "fill":
                    flood_fill(canvas, pos, current_color)
                    status_message = "Flood fill applied"
                    continue

                if current_tool == "text":
                    text_mode = True
                    text_pos = pos
                    text_value = ""
                    status_message = "Typing text: Enter to confirm, Esc to cancel"
                    continue

                drawing = True
                start_pos = pos
                last_pos = pos

                if current_tool == "pencil":
                    pygame.draw.circle(canvas, current_color, pos, max(1, brush_size // 2))
                elif current_tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, pos, brush_size * 2)

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing and start_pos and on_canvas(event.pos):
                    end_pos = canvas_pos(event.pos)
                    if current_tool in SHAPE_TOOLS:
                        SHAPE_DRAWERS[current_tool](canvas, start_pos, end_pos, current_color, brush_size)

                drawing = False
                start_pos = None
                last_pos = None

            if event.type == pygame.MOUSEMOTION and drawing and on_canvas(event.pos):
                pos = canvas_pos(event.pos)
                if current_tool == "pencil":
                    pygame.draw.line(canvas, current_color, last_pos, pos, brush_size)
                    last_pos = pos
                elif current_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, pos, brush_size * 4)
                    pygame.draw.circle(canvas, WHITE, pos, brush_size * 2)
                    last_pos = pos

        screen.fill(WHITE)
        screen.blit(canvas, (0, PANEL_H))

        if drawing and start_pos and current_tool in SHAPE_TOOLS:
            mouse = pygame.mouse.get_pos()
            if on_canvas(mouse):
                preview = canvas.copy()
                SHAPE_DRAWERS[current_tool](preview, start_pos, canvas_pos(mouse), current_color, brush_size)
                screen.blit(preview, (0, PANEL_H))

        if text_mode:
            draw_text_preview(text_value, text_pos)

        draw_panel(current_color, current_tool, brush_size, status_message)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
