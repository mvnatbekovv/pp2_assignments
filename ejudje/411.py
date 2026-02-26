import json

source = json.loads(input())
patch_obj = json.loads(input())

def apply(source, patch):
    for key, val in patch.items():
        if val is None:
            source.pop(key, None)
        elif isinstance(val, dict) and isinstance(source.get(key), dict):
            apply(source[key], val)
        else:
            source[key] = val

apply(source, patch_obj)

print(json.dumps(source, separators=(',', ':'), sort_keys=True))