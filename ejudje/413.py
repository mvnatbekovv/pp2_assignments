import json
import sys

def parse_query(q: str):
    tokens = []
    i = 0
    n = len(q)
    while i < n:
        if q[i] == '.':
            i += 1
            continue
        if q[i] == '[':
            j = q.find(']', i)
            if j == -1:
                return None
            idx_str = q[i + 1:j]
            if not idx_str.isdigit():
                return None
            tokens.append(int(idx_str))
            i = j + 1
        else:
            j = i
            while j < n and q[j] not in '.[':
                j += 1
            if j == i:
                return None
            tokens.append(q[i:j])
            i = j
    return tokens

def resolve(data, tokens):
    cur = data
    for t in tokens:
        if isinstance(t, str):
            if isinstance(cur, dict) and t in cur:
                cur = cur[t]
            else:
                return None, False
        else:  # int index
            if isinstance(cur, list) and 0 <= t < len(cur):
                cur = cur[t]
            else:
                return None, False
    return cur, True

data = json.loads(sys.stdin.readline().strip())
q = int(sys.stdin.readline().strip())

for _ in range(q):
    query = sys.stdin.readline().strip()
    tokens = parse_query(query)
    if tokens is None:
        print("NOT_FOUND")
        continue
    value, ok = resolve(data, tokens)
    if not ok:
        print("NOT_FOUND")
    else:
        print(json.dumps(value, separators=(',', ':')))