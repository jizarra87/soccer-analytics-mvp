import pandas as pd

def calculate_player_stats(events_df, players_df):
    if events_df.empty:
        return pd.DataFrame()

    # Count events per player
    stats = events_df.groupby(["player_id", "event_type"]).size().unstack(fill_value=0)

    # Rename columns (optional safety)
    stats = stats.rename(columns={
        "pass": "passes",
        "shot": "shots",
        "goal": "goals",
        "tackle": "tackles"
    })

    # Merge with player names
    stats = stats.merge(players_df, on="player_id", how="left")

    return stats