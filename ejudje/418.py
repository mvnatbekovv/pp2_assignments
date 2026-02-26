x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

t = -y1 / (-y2 - y1)
x = x1 + t * (x2 - x1)

print(f"{x:.10f} 0.0000000000")