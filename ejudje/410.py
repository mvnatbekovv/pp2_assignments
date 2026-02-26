def l(lst, n):
    for _ in range(n):        
        for it in lst:      
            yield it


lst = input().split()
n = int(input())

for elem in l(lst, n):
    print(elem, end=" ")