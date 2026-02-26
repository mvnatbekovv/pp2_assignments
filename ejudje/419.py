import math

r = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

dx = x2 - x1
dy = y2 - y1

d = math.hypot(dx, dy)
d1 = math.hypot(x1, y1)
d2 = math.hypot(x2, y2)

t = -(x1 * dx + y1 * dy) / (dx * dx + dy * dy)

if t < 0:
    cd = d1
elif t > 1:
    cd = d2
else:
    px = x1 + t * dx
    py = y1 + t * dy
    cd = math.hypot(px, py)

if cd >= r:
    print(f"{d:.10f}")
else:
    th = math.acos((x1 * x2 + y1 * y2) / (d1 * d2))
    a = th - math.acos(r / d1) - math.acos(r / d2)
    l = math.sqrt(d1 * d1 - r * r) + math.sqrt(d2 * d2 - r * r) + r * a
    print(f"{l:.10f}")