def countdown(n):
    while n >= 0:
        yield n
        n -= 1


n = int(input("Enter N: "))

for value in countdown(n):
    print(value)