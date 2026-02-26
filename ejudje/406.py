def fibonacci(n):
    a = 0
    b = 1
    count = 0
    while count < n:
        yield a
        a, b = b, a + b
        count += 1

n = int(input())

first = True
for num in fibonacci(n):
    if first:
        print(num, end="")
        first = False
    else:
        print("," + str(num), end="")