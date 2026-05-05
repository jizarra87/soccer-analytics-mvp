import streamlit as st
from src.db import init_db, get_connection
import pandas as pd
import time
from src.stats import calculate_player_stats
from src.report import generate_player_report
import os
from src.tracking import track_players_and_save
# Initialize DB
init_db()

st.title("⚽ Soccer Analytics MVP")

# -------------------------
# Load Matches & Players
# -------------------------
conn = get_connection()
matches = pd.read_sql("SELECT * FROM dim_matches", conn)
players = pd.read_sql("SELECT * FROM dim_players", conn)
conn.close()

# -------------------------
# SESSION STATE (TIMER)
# -------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "current_time" not in st.session_state:
    st.session_state.current_time = 0

# =========================
# 🎥 MATCH ANALYSIS (MAIN UX)
# =========================
st.header("🎥 Match Analysis")

col_video, col_controls = st.columns([2, 1])

# -------------------------
# LEFT → VIDEO
# -------------------------
with col_video:
    st.subheader("Video")

video_file = st.file_uploader("Upload Match Video", type=["mp4", "mov", "avi"])

video_path = None

if video_file:
    os.makedirs("videos", exist_ok=True)

    video_path = f"videos/{video_file.name}"

    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    st.video(video_path)
    st.success(f"Video saved: {video_path}")

# -------------------------
# RIGHT → CONTROLS
# -------------------------
with col_controls:
    st.subheader("Controls")

    if not matches.empty and not players.empty:

        selected_match = st.selectbox(
            "Match",
            matches["match_id"],
            format_func=lambda x: f"Match {x} vs {matches[matches.match_id==x]['opponent'].values[0]}"
        )

        selected_player = st.selectbox(
            "Player",
            players["player_id"],
            format_func=lambda x: players[players.player_id==x]["name"].values[0]
        )
    if video_path:
        if st.button("🚀 Analyze Video (Tracking)"):
            with st.spinner("Running tracking... this may take time"):
                track_players_and_save(video_path, match_id=selected_match)

        st.success("Tracking completed!")

        # TIMER
        st.markdown("### ⏱️ Timer")

        if st.button("▶️ Start"):
            st.session_state.start_time = time.time()

        if st.session_state.start_time:
            current_time = int(time.time() - st.session_state.start_time)
            st.write(f"⏱️ {current_time} sec")

        st.write(f"Time: {st.session_state.current_time} sec")

        # SAVE EVENT
        def save_event(event_type):
            if st.session_state.start_time:
                event_time = int(time.time() - st.session_state.start_time)
            else:
                event_time = 0

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO fact_events (match_id, player_id, event_type, event_time_seconds, team)
                VALUES (?, ?, ?, ?, ?)
                """,
                (selected_match, selected_player, event_type, event_time, "our_team")
            )
            conn.commit()
            conn.close()

            st.success(f"{event_type} saved at {event_time}s!")
        st.markdown("### 🎯 Events")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔵 Pass", use_container_width=True):
                save_event("pass")
            if st.button("🟢 Goal", use_container_width=True):
                save_event("goal")

        with col2:
            if st.button("🟠 Shot", use_container_width=True):
                save_event("shot")
            if st.button("🔴 Tackle", use_container_width=True):
                save_event("tackle")

    else:
        st.warning("Create match and players first.")

# =========================
# ⚙️ SETUP (below)
# =========================
st.header("⚙️ Setup")

col_setup1, col_setup2 = st.columns(2)

# Create Match
with col_setup1:
    st.subheader("Create Match")

    opponent = st.text_input("Opponent")
    match_date = st.date_input("Match Date")

    if st.button("Create Match"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dim_matches (opponent, date) VALUES (?, ?)",
            (opponent, str(match_date))
        )
        conn.commit()
        conn.close()
        st.success("Match created!")

# Add Player
with col_setup2:
    st.subheader("Add Player")

    player_name = st.text_input("Player Name")
    position = st.text_input("Position")

    if st.button("Add Player"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dim_players (name, position) VALUES (?, ?)",
            (player_name, position)
        )
        conn.commit()
        conn.close()
        st.success("Player added!")

# =========================
# 🗂️ EVENT TIMELINE
# =========================
st.header("🗂️ Event Timeline")

conn = get_connection()
events_df = pd.read_sql("SELECT * FROM fact_events", conn)
players_df = pd.read_sql("SELECT * FROM dim_players", conn)
conn.close()

if not events_df.empty:

    events_df = events_df.merge(players_df, on="player_id", how="left")

    player_filter = st.selectbox(
        "Filter by Player",
        ["All"] + players_df["name"].tolist()
    )

    if player_filter != "All":
        events_df = events_df[events_df["name"] == player_filter]

    st.dataframe(events_df.sort_values("event_time_seconds"))

    # DELETE
    st.subheader("🗑️ Delete Event")

    selected_event_id = st.selectbox(
        "Select Event",
        events_df["event_id"].tolist()
    )

    if st.button("Delete Event"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fact_events WHERE event_id = ?", (selected_event_id,))
        conn.commit()
        conn.close()
        st.success("Event deleted!")
        st.rerun()

else:
    st.info("No events yet.")

# =========================
# 📊 STATS
# =========================
st.header("📊 Player Stats")

if not events_df.empty:

    stats_df = calculate_player_stats(events_df, players_df)

    st.dataframe(stats_df)

    if "shots" in stats_df.columns:
        st.bar_chart(stats_df[["name", "shots"]].set_index("name"))

else:
    st.info("No stats yet.")

# =========================
# 📄 REPORT
# =========================
st.header("📄 Player Report")

if not players.empty:

    selected_player_report = st.selectbox(
        "Select Player",
        players["player_id"],
        format_func=lambda x: players[players.player_id==x]["name"].values[0]
    )

    if st.button("Generate Report"):

        player_row = players[players.player_id == selected_player_report].iloc[0]
        player_events = events_df[events_df.player_id == selected_player_report]

        stats = {
            "passes": len(player_events[player_events.event_type == "pass"]),
            "shots": len(player_events[player_events.event_type == "shot"]),
            "goals": len(player_events[player_events.event_type == "goal"]),
            "tackles": len(player_events[player_events.event_type == "tackle"]),
        }

        output_path = f"{player_row['name']}_report.pdf"

        generate_player_report(
            player_name=player_row["name"],
            position=player_row["position"],
            stats=stats,
            output_path=output_path
        )

        st.success(f"Report generated: {output_path}")

# =========================
# 🎯 TRACK → PLAYER MAPPING
# =========================
st.header("🎯 Map Tracks to Players")

conn = get_connection()

tracks_df = pd.read_sql("""
SELECT DISTINCT track_id
FROM fact_player_tracks
""", conn)

players_df = pd.read_sql("SELECT * FROM dim_players", conn)

conn.close()

if not tracks_df.empty:

    for track_id in tracks_df["track_id"]:

        col1, col2 = st.columns([1,2])

        with col1:
            st.write(f"Track ID: {track_id}")

        with col2:
            selected_player = st.selectbox(
                f"Assign Player to Track {track_id}",
                players_df["player_id"],
                key=f"track_{track_id}",
                format_func=lambda x: players_df[players_df.player_id==x]["name"].values[0]
            )

            if st.button(f"Save Mapping {track_id}"):
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO dim_track_player_map (match_id, track_id, player_id)
                VALUES (?, ?, ?)
                """, (1, track_id, selected_player))

                conn.commit()
                conn.close()

                st.success(f"Track {track_id} mapped!")

st.header("🧹 Reset Database")

if st.button("⚠️ Reset All Data"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM fact_events")
    cursor.execute("DELETE FROM fact_player_tracks")
    cursor.execute("DELETE FROM dim_track_player_map")
    cursor.execute("DELETE FROM dim_players")
    cursor.execute("DELETE FROM dim_matches")

    conn.commit()
    conn.close()

    st.success("Database cleared!")
    st.rerun()