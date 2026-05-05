from ultralytics import YOLO
import cv2
from src.db import get_connection

model = YOLO("yolov8n.pt")


def track_players_and_save(video_path: str, match_id: int):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    conn = get_connection()
    cursor = conn.cursor()
    
    frame_skip = 3
    frame_number = 0

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break
            
        if frame_number % frame_skip != 0:
            frame_number += 1
            continue

        results = model.track(
                    frame,
                    persist=True,
                    tracker="bytetrack.yaml",  # ⬅️ NEW
                    classes=[0],
                    conf=0.5,
                    iou=0.5,
                    verbose=False
                )

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes

            for i, (box, track_id) in enumerate(zip(boxes.xyxy, boxes.id)):
                x1, y1, x2, y2 = map(int, box.tolist())
                track_id = int(track_id)
                width = x2 - x1
                height = y2 - y1

                # ⬇️ ADD THIS FILTER
                if width < 30 or height < 30:
                    continue
                confidence = float(boxes.conf[i]) if boxes.conf is not None else None

                cursor.execute(
                    """
                    INSERT INTO fact_player_tracks (
                        match_id,
                        frame_number,
                        track_id,
                        x1, y1, x2, y2,
                        confidence
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        match_id,
                        frame_number,
                        track_id,
                        x1, y1, x2, y2,
                        confidence
                    )
                )

        frame_number += 1

    conn.commit()
    conn.close()
    cap.release()

    print("Tracking saved successfully.")