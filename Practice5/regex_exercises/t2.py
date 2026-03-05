import re

s = input().strip()
print("Yes" if re.fullmatch(r"ab{2,3}", s) else "No")