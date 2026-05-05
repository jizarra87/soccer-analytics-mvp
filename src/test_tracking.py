from src.tracking import track_players_and_save
from src.db import init_db


# Initialize DB
init_db()


track_players_and_save("videos\Veo _ UPSL vs. Deportivo Lake Mary - Google Chrome 2026-04-28 22-53-18.mp4", match_id=1)