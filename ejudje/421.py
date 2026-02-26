import sys
import importlib

n = int(sys.stdin.readline())
for _ in range(n):
    m, a = sys.stdin.readline().split()
    try:
        mod = importlib.import_module(m)
    except ModuleNotFoundError:
        print("MODULE_NOT_FOUND")
        continue
    if not hasattr(mod, a):
        print("ATTRIBUTE_NOT_FOUND")
        continue
    v = getattr(mod, a)
    print("CALLABLE" if callable(v) else "VALUE")