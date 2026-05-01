import math
from collections import deque
from typing import Tuple

import pygame

Color = Tuple[int, int, int]
Point = Tuple[int, int]


def normalize_rect(start_pos: Point, end_pos: Point) -> pygame.Rect:
    x = min(start_pos[0], end_pos[0])
    y = min(start_pos[1], end_pos[1])
    w = abs(end_pos[0] - start_pos[0])
    h = abs(end_pos[1] - start_pos[1])
    return pygame.Rect(x, y, w, h)


def draw_rectangle(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    pygame.draw.rect(surface, color, normalize_rect(start_pos, end_pos), brush_size)


def draw_square(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    side = min(abs(dx), abs(dy))
    ex = start_pos[0] + (side if dx >= 0 else -side)
    ey = start_pos[1] + (side if dy >= 0 else -side)
    pygame.draw.rect(surface, color, normalize_rect(start_pos, (ex, ey)), brush_size)


def draw_circle(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    cx = (start_pos[0] + end_pos[0]) // 2
    cy = (start_pos[1] + end_pos[1]) // 2
    radius = int(math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]) // 2)
    pygame.draw.circle(surface, color, (cx, cy), max(1, radius), brush_size)


def draw_line(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    pygame.draw.line(surface, color, start_pos, end_pos, brush_size)
    radius = max(1, brush_size // 2)
    pygame.draw.circle(surface, color, start_pos, radius)
    pygame.draw.circle(surface, color, end_pos, radius)


def draw_right_triangle(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    a = start_pos
    b = (end_pos[0], start_pos[1])
    c = (start_pos[0], end_pos[1])
    pygame.draw.polygon(surface, color, [a, b, c], brush_size)


def draw_equilateral_triangle(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    base_len = abs(end_pos[0] - start_pos[0])
    if base_len == 0:
        return
    height = int(base_len * math.sqrt(3) / 2)
    x1 = min(start_pos[0], end_pos[0])
    x2 = max(start_pos[0], end_pos[0])
    y_base = start_pos[1]
    mid_x = (x1 + x2) // 2
    direction = -1 if end_pos[1] < start_pos[1] else 1
    pygame.draw.polygon(surface, color, [(x1, y_base), (x2, y_base), (mid_x, y_base + direction * height)], brush_size)


def draw_rhombus(surface: pygame.Surface, start_pos: Point, end_pos: Point, color: Color, brush_size: int) -> None:
    rect = normalize_rect(start_pos, end_pos)
    mid_x = rect.centerx
    mid_y = rect.centery
    points = [(mid_x, rect.top), (rect.right, mid_y), (mid_x, rect.bottom), (rect.left, mid_y)]
    pygame.draw.polygon(surface, color, points, brush_size)


def flood_fill(surface: pygame.Surface, start_pos: Point, new_color: Color) -> None:
    width, height = surface.get_size()
    x, y = start_pos
    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))[:3]
    replacement = tuple(new_color)
    if target_color == replacement:
        return

    queue = deque([(x, y)])
    visited = set()

    while queue:
        px, py = queue.popleft()
        if (px, py) in visited:
            continue
        if not (0 <= px < width and 0 <= py < height):
            continue
        if surface.get_at((px, py))[:3] != target_color:
            continue

        surface.set_at((px, py), replacement)
        visited.add((px, py))

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


SHAPE_DRAWERS = {
    "rect": draw_rectangle,
    "square": draw_square,
    "circle": draw_circle,
    "line": draw_line,
    "rtriangle": draw_right_triangle,
    "eqtriangle": draw_equilateral_triangle,
    "rhombus": draw_rhombus,
}
