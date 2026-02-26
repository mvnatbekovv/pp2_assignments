import math

r = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

dx = x2 - x1
dy = y2 - y1
a = dx * dx + dy * dy
b = 2 * (dx * x1 + dy * y1)
c = x1 * x1 + y1 * y1 - r * r

discriminant = b * b - 4 * a * c
if discriminant <= 0:
    print("0.0000000000")
else:
    sqrt_d = math.sqrt(discriminant)
    t1 = (-b - sqrt_d) / (2 * a)
    t2 = (-b + sqrt_d) / (2 * a)
    t_in, t_out = min(t1, t2), max(t1, t2)

    t_start = max(0.0, t_in)
    t_end = min(1.0, t_out)

    if t_start >= t_end:
        length = 0.0
    else:
        length = math.hypot(dx, dy) * (t_end - t_start)

    print(f"{length:.10f}")