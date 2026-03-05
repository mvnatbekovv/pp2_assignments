import re

s = input().strip()
snake = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
print(snake)