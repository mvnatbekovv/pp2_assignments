import os

os.makedirs("test/subdir", exist_ok=True)
print(os.listdir("."))
print(os.getcwd())