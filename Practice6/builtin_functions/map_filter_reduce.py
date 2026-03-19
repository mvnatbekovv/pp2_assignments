from functools import reduce

nums = [1,2,3,4]

print(list(map(lambda x: x*2, nums)))
print(list(filter(lambda x: x%2==0, nums)))
print(reduce(lambda x,y: x+y, nums))