g = 0

def o(cmds):
    n = 0
    def i():
        nonlocal n
        global g
        for s, v in cmds:
            v = int(v)
            if s == "global":
                g += v
            elif s == "nonlocal":
                n += v
            elif s == "local":
                x = v
        return n
    n = i()
    return n

nf = o([input().split() for _ in range(int(input()))])
print(g, nf)