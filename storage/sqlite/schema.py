from __future__ import annotations


SQLITE_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY,
        nickname TEXT NOT NULL,
        started_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        size INTEGER NOT NULL,
        winner TEXT,
        game_over INTEGER NOT NULL,
        data TEXT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS game_states (
        game_id TEXT PRIMARY KEY,
        state_json TEXT NOT NULL,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS game_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        action_index INTEGER NOT NULL,
        action_time TEXT,
        actor TEXT,
        kind TEXT,
        target TEXT,
        direction TEXT,
        description TEXT,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        UNIQUE (game_id, action_index)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_game_actions_game_id ON game_actions (game_id)",
    """
    CREATE TABLE IF NOT EXISTS game_statistics (
        game_id TEXT PRIMARY KEY,
        turns INTEGER NOT NULL,
        player_hits INTEGER NOT NULL,
        enemy_hits INTEGER NOT NULL,
        player_misses INTEGER NOT NULL,
        enemy_misses INTEGER NOT NULL,
        total_hits INTEGER NOT NULL,
        total_misses INTEGER NOT NULL,
        hit_miss_ratio REAL NOT NULL,
        player_ships_left INTEGER NOT NULL,
        enemy_ships_left INTEGER NOT NULL,
        player_ships_lost INTEGER NOT NULL,
        enemy_ships_lost INTEGER NOT NULL,
        powerups_used INTEGER NOT NULL,
        cells_moved INTEGER NOT NULL,
        asteroid_hits INTEGER NOT NULL,
        player_asteroid_hits INTEGER NOT NULL,
        enemy_asteroid_hits INTEGER NOT NULL,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS game_ships (
        game_id TEXT NOT NULL,
        owner TEXT NOT NULL,
        ship_id INTEGER NOT NULL,
        ship_type TEXT NOT NULL,
        length INTEGER NOT NULL,
        cells_json TEXT NOT NULL,
        hits_json TEXT NOT NULL,
        hits_count INTEGER NOT NULL,
        sunk INTEGER NOT NULL,
        power_used INTEGER NOT NULL,
        disabled_turns INTEGER NOT NULL,
        PRIMARY KEY (game_id, owner, ship_id),
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS game_asteroids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT NOT NULL,
        owner TEXT NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        dx INTEGER NOT NULL,
        dy INTEGER NOT NULL,
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_game_asteroids_game_id ON game_asteroids (game_id)",
]
