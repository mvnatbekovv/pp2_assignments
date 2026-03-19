names = ["A", "B"]
scores = [90, 80]

for i, name in enumerate(names):
    print(i, name)

for name, score in zip(names, scores):
    print(name, score)