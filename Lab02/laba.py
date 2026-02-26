n = int(input())

doc = {}

for _ in range(n):

    c = input().split()
    
    a= c[0]
    key = c[1]
    
    if a == "set":

        val = c[2]
        doc[key] = val
        
    elif a == "get":

        if key in doc:
            print(doc[key])
        else:
            print(f"KE: no key {key} found in the document") 
            print("hello")
