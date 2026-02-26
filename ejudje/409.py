def powers_of_two(n):
    for i in range(0, n + 1):
        yield 2 ** i

n = int(input())

for num in powers_of_two(n):
    print(num, end=" ")