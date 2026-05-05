import sqlite3
import os

DB_PATH = "data/soccer_mvp.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        opponent TEXT,
        date TEXT
    )
    """)

    # Players table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        position TEXT
    )
    """)

    # Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        event_type TEXT,
        event_time_seconds INTEGER,
        team TEXT,
        FOREIGN KEY(match_id) REFERENCES matches(match_id),
        FOREIGN KEY(player_id) REFERENCES players(player_id)
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_player_tracks (
            track_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            frame_number INTEGER,
            track_id INTEGER,
            x1 INTEGER,
            y1 INTEGER,
            x2 INTEGER,
            y2 INTEGER,
            confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)


    cursor.execute("""
            CREATE TABLE IF NOT EXISTS dim_track_player_map (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                track_id INTEGER,
                player_id INTEGER
            )
            """)
    conn.commit()
    conn.close()