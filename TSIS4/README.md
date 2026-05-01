# TSIS4: Snake Game

Pygame Snake with PostgreSQL leaderboard, personal best, poison food, power-ups, obstacles from level 3, settings and screens.

## Install

```bash
pip install pygame psycopg2-binary
```

## PostgreSQL setup

Create database:

```bash
createdb -U postgres -h localhost snake
```

Edit `config.py` and put your PostgreSQL password.

Tables are created automatically when you run the game.

## Run

```bash
python3 main.py
```

## Controls

- Arrow keys / WASD: move snake
- Enter: confirm username
- Escape: back / quit current screen

## Files

- `main.py` — game and screens
- `db.py` — PostgreSQL functions
- `settings.py` — JSON settings helpers
- `config.py` — PostgreSQL connection data
- `settings.json` — saved preferences
