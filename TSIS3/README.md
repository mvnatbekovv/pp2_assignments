# TSIS3 Racer Game

Advanced Pygame racer for TSIS3.

## Run

```bash
pip install pygame
python3 main.py
```

## Controls

- Arrow keys or WASD: move the car
- Escape: leave current game/screen
- Type username on the main menu before pressing Play

## Implemented requirements

- Main Menu, Settings, Leaderboard, Game Over screens
- Username entry before game start
- Dynamic traffic cars
- Road obstacles: barriers, potholes, oil
- Dynamic road events: speed bump and nitro strip
- Safe spawn logic so objects do not appear directly on top of the player
- Difficulty scaling by distance and selected difficulty
- Coins with different values
- Score = distance + coin bonuses
- Distance meter and finish target
- Persistent top 10 leaderboard in `leaderboard.json`
- Settings stored in `settings.json`: sound, car color, difficulty
- Power-ups: Nitro, Shield, Repair
- Active power-up and remaining time shown on screen
