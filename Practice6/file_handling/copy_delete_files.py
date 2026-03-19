import shutil, os

shutil.copy("example.txt", "copy.txt")

if os.path.exists("copy.txt"):
    os.remove("copy.txt")