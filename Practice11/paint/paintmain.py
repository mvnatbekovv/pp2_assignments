import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
PANEL_H = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

COLORS = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 200, 0),
    (0, 0, 255), (255, 165, 0), (255, 255, 0), (128, 0, 128),
    (0, 255, 255), (255, 20, 147), (139, 69, 19), (128, 128, 128)
]

# Extended tool list with new shapes
TOOLS = ["pencil", "eraser", "rect", "square", "circle",
         "rtriangle", "eqtriangle", "rhombus"]

TOOL_LABELS = {
    "pencil":     "Pencil",
    "eraser":     "Eraser",
    "rect":       "Rect",
    "square":     "Square",
    "circle":     "Circle",
    "rtriangle":  "RTri",
    "eqtriangle": "EqTri",
    "rhombus":    "Rhombus",
}


# ──────────────────────────────────────────────
#  Shape drawing helpers
# ──────────────────────────────────────────────

def draw_rectangle(surface, start_pos, end_pos, color, brush_size):
    """Draw a free rectangle defined by two corner points."""
    x = min(start_pos[0], end_pos[0])
    y = min(start_pos[1], end_pos[1])
    w = abs(end_pos[0] - start_pos[0])
    h = abs(end_pos[1] - start_pos[1])
    pygame.draw.rect(surface, color, (x, y, w, h), brush_size)


def draw_square(surface, start_pos, end_pos, color, brush_size):
    """
    Draw a square. The side length equals the shorter dimension
    of the bounding box formed by start_pos and end_pos.
    """
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    side = min(abs(dx), abs(dy))
    # Preserve direction so the square follows the mouse
    sx = start_pos[0]
    sy = start_pos[1]
    ex = sx + (side if dx >= 0 else -side)
    ey = sy + (side if dy >= 0 else -side)
    x = min(sx, ex)
    y = min(sy, ey)
    pygame.draw.rect(surface, color, (x, y, side, side), brush_size)


def draw_circle(surface, start_pos, end_pos, color, brush_size):
    """Draw a circle whose diameter spans start_pos → end_pos."""
    cx = (start_pos[0] + end_pos[0]) // 2
    cy = (start_pos[1] + end_pos[1]) // 2
    r = int(((end_pos[0] - start_pos[0]) ** 2 +
             (end_pos[1] - start_pos[1]) ** 2) ** 0.5 // 2)
    pygame.draw.circle(surface, color, (cx, cy), max(1, r), brush_size)


def draw_right_triangle(surface, start_pos, end_pos, color, brush_size):
    """
    Draw a right triangle.
    - Right angle is at start_pos (top-left corner of the bounding box).
    - The two legs are horizontal and vertical.
    - The hypotenuse connects the end of the horizontal leg to the end
      of the vertical leg.
    Vertices:
      A = start_pos                     (right angle)
      B = (end_pos[0], start_pos[1])    (end of horizontal leg)
      C = (start_pos[0], end_pos[1])    (end of vertical leg)
    """
    A = start_pos
    B = (end_pos[0], start_pos[1])
    C = (start_pos[0], end_pos[1])
    pygame.draw.polygon(surface, color, [A, B, C], brush_size)


def draw_equilateral_triangle(surface, start_pos, end_pos, color, brush_size):
    """
    Draw an equilateral triangle.
    The base runs from start_pos to (end_pos[0], start_pos[1]).
    The apex is directly above (or below) the midpoint of the base
    at height = base * sqrt(3) / 2.
    Direction (up/down) follows the sign of end_pos[1] - start_pos[1].
    """
    base_len = abs(end_pos[0] - start_pos[0])
    if base_len == 0:
        return
    height = int(base_len * math.sqrt(3) / 2)

    # Base left and right
    x1 = min(start_pos[0], end_pos[0])
    x2 = max(start_pos[0], end_pos[0])
    y_base = start_pos[1]
    mid_x = (x1 + x2) // 2

    # Apex goes upward if mouse dragged upward, downward otherwise
    direction = -1 if (end_pos[1] - start_pos[1]) <= 0 else 1
    apex = (mid_x, y_base + direction * height)

    A = (x1, y_base)
    B = (x2, y_base)
    C = apex
    pygame.draw.polygon(surface, color, [A, B, C], brush_size)


def draw_rhombus(surface, start_pos, end_pos, color, brush_size):
    """
    Draw a rhombus (diamond).
    The diagonals span the bounding box of start_pos and end_pos:
      - Horizontal diagonal: left-mid to right-mid
      - Vertical diagonal:   top-mid to bottom-mid
    """
    x1 = min(start_pos[0], end_pos[0])
    y1 = min(start_pos[1], end_pos[1])
    x2 = max(start_pos[0], end_pos[0])
    y2 = max(start_pos[1], end_pos[1])
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2

    top    = (mid_x, y1)
    right  = (x2,    mid_y)
    bottom = (mid_x, y2)
    left   = (x1,    mid_y)
    pygame.draw.polygon(surface, color, [top, right, bottom, left], brush_size)


# ──────────────────────────────────────────────
#  Tool panel
# ──────────────────────────────────────────────

def draw_panel(surface, current_color, current_tool, brush_size):
    pygame.draw.rect(surface, (220, 220, 220), (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(surface, (150, 150, 150), (0, PANEL_H), (WIDTH, PANEL_H), 2)

    # Color swatches
    for i, color in enumerate(COLORS):
        rect = pygame.Rect(10 + i * 38, 10, 32, 32)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        if color == current_color:
            pygame.draw.rect(surface, (255, 255, 0), rect, 3)

    font = pygame.font.SysFont("Arial", 13)

    # Tool buttons — two rows to fit all 8 tools
    tools_row1 = TOOLS[:4]
    tools_row2 = TOOLS[4:]
    button_w = 68
    x_start = 490

    for i, tool in enumerate(tools_row1):
        x = x_start + i * (button_w + 4)
        y = 2
        btn_color = (100, 200, 100) if tool == current_tool else (180, 180, 180)
        pygame.draw.rect(surface, btn_color, (x, y, button_w, 26), border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, button_w, 26), 1, border_radius=4)
        text = font.render(TOOL_LABELS[tool], True, (0, 0, 0))
        surface.blit(text, (x + 4, y + 7))

    for i, tool in enumerate(tools_row2):
        x = x_start + i * (button_w + 4)
        y = 32
        btn_color = (100, 200, 100) if tool == current_tool else (180, 180, 180)
        pygame.draw.rect(surface, btn_color, (x, y, button_w, 24), border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, button_w, 24), 1, border_radius=4)
        text = font.render(TOOL_LABELS[tool], True, (0, 0, 0))
        surface.blit(text, (x + 4, y + 6))

    # Brush size indicator
    size_font = pygame.font.SysFont("Arial", 16)
    size_text = size_font.render(f"Size: {brush_size}", True, (0, 0, 0))
    surface.blit(size_text, (10, 44))


# ──────────────────────────────────────────────
#  Main loop
# ──────────────────────────────────────────────

# Shape tools that are drawn on mouse-release (not while dragging)
SHAPE_TOOLS = {"rect", "square", "circle", "rtriangle", "eqtriangle", "rhombus"}

# Map tool names to their drawing functions
SHAPE_DRAW = {
    "rect":       draw_rectangle,
    "square":     draw_square,
    "circle":     draw_circle,
    "rtriangle":  draw_right_triangle,
    "eqtriangle": draw_equilateral_triangle,
    "rhombus":    draw_rhombus,
}


def main():
    canvas = pygame.Surface((WIDTH, HEIGHT - PANEL_H))
    canvas.fill((255, 255, 255))

    current_color = (0, 0, 0)
    current_tool = "pencil"
    brush_size = 5

    drawing = False
    start_pos = None
    last_pos = None

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Scroll wheel changes brush size
            if event.type == pygame.MOUSEWHEEL:
                brush_size = max(1, min(50, brush_size + event.y))

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if my < PANEL_H:
                    # Check color swatches
                    for i, color in enumerate(COLORS):
                        rect = pygame.Rect(10 + i * 38, 10, 32, 32)
                        if rect.collidepoint(mx, my):
                            current_color = color

                    # Check tool buttons — row 1
                    button_w = 68
                    x_start = 490
                    for i, tool in enumerate(TOOLS[:4]):
                        x = x_start + i * (button_w + 4)
                        if pygame.Rect(x, 2, button_w, 26).collidepoint(mx, my):
                            current_tool = tool
                    # Check tool buttons — row 2
                    for i, tool in enumerate(TOOLS[4:]):
                        x = x_start + i * (button_w + 4)
                        if pygame.Rect(x, 32, button_w, 24).collidepoint(mx, my):
                            current_tool = tool

                else:
                    # Start drawing on the canvas
                    drawing = True
                    start_pos = (mx, my - PANEL_H)
                    last_pos = start_pos

                    if current_tool == "pencil":
                        pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, (255, 255, 255), start_pos, brush_size * 3)

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing and start_pos:
                    mx, my = event.pos
                    end_pos = (mx, my - PANEL_H)

                    # Finalize shape tools on mouse-up
                    if current_tool in SHAPE_TOOLS:
                        SHAPE_DRAW[current_tool](canvas, start_pos, end_pos,
                                                 current_color, brush_size)

                drawing = False
                start_pos = None
                last_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos

                if my > PANEL_H:
                    pos = (mx, my - PANEL_H)

                    if current_tool == "pencil":
                        # Draw continuous line while mouse moves
                        pygame.draw.line(canvas, current_color, last_pos, pos, brush_size * 2)
                        pygame.draw.circle(canvas, current_color, pos, brush_size)
                        last_pos = pos

                    elif current_tool == "eraser":
                        # Erase continuously while mouse moves
                        pygame.draw.line(canvas, (255, 255, 255), last_pos, pos, brush_size * 6)
                        pygame.draw.circle(canvas, (255, 255, 255), pos, brush_size * 3)
                        last_pos = pos

        # Render canvas
        screen.fill((255, 255, 255))
        screen.blit(canvas, (0, PANEL_H))

        # Live preview for shape tools while dragging
        if drawing and start_pos and current_tool in SHAPE_TOOLS:
            mx, my = pygame.mouse.get_pos()
            end_pos = (mx, my - PANEL_H)
            preview = canvas.copy()
            SHAPE_DRAW[current_tool](preview, start_pos, end_pos,
                                     current_color, brush_size)
            screen.blit(preview, (0, PANEL_H))

        draw_panel(screen, current_color, current_tool, brush_size)

        pygame.display.flip()
        clock.tick(60)


main()
