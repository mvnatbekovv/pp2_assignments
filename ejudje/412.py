import json

obj1 = json.loads(input())
obj2 = json.loads(input())

differences = []

def serialize(val):
    if val == "<missing>":
        return "<missing>"
    return json.dumps(val, separators=(',', ':'))

def deep_diff(o1, o2, path=""):
    keys = set()
    if isinstance(o1, dict):
        keys.update(o1.keys())
    if isinstance(o2, dict):
        keys.update(o2.keys())
    
    for key in keys:
        new_path = f"{path}.{key}" if path else key
        val1 = o1.get(key, "<missing>") if isinstance(o1, dict) else "<missing>"
        val2 = o2.get(key, "<missing>") if isinstance(o2, dict) else "<missing>"
        
        if isinstance(val1, dict) and isinstance(val2, dict):
            deep_diff(val1, val2, new_path)
        elif val1 != val2:
            differences.append(f"{new_path} : {serialize(val1)} -> {serialize(val2)}")

deep_diff(obj1, obj2)

if differences:
    for diff in sorted(differences):
        print(diff)
else:
    print("No differences")