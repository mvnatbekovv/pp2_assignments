import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": [40, 120, 255],
    "difficulty": "Normal"
}

DIFFICULTY_CONFIG = {
    "Easy": {"traffic_rate": 0.012, "obstacle_rate": 0.009, "speed": 4.0, "density_scale": 0.55},
    "Normal": {"traffic_rate": 0.018, "obstacle_rate": 0.014, "speed": 5.0, "density_scale": 0.8},
    "Hard": {"traffic_rate": 0.026, "obstacle_rate": 0.020, "speed": 6.0, "density_scale": 1.05},
}


def load_json(path, default):
    try:
        if not path.exists():
            save_json(path, default)
            return default.copy() if isinstance(default, dict) else list(default)
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default.copy() if isinstance(default, dict) else list(default)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_settings():
    data = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    if merged["difficulty"] not in DIFFICULTY_CONFIG:
        merged["difficulty"] = "Normal"
    if not isinstance(merged.get("car_color"), list) or len(merged["car_color"]) != 3:
        merged["car_color"] = DEFAULT_SETTINGS["car_color"]
    return merged


def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


def load_leaderboard():
    scores = load_json(LEADERBOARD_FILE, [])
    if not isinstance(scores, list):
        return []
    return sorted(scores, key=lambda item: item.get("score", 0), reverse=True)[:10]


def add_score(username, score, distance, coins, difficulty=None):
    scores = load_leaderboard()
    scores.append({
        "name": username or "Player",
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })
    scores = sorted(scores, key=lambda item: item.get("score", 0), reverse=True)[:10]
    save_json(LEADERBOARD_FILE, scores)
    return scores
