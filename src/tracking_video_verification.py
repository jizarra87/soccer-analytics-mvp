from ultralytics import YOLO
import cv2

model = YOLO("yolov8m.pt")  # you can change to yolov8m.pt later


def track_players_debug(video_path: str):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_number = 0

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        # Run tracking
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",  # use default first for stability
            classes=[0],               # only persons
            conf=0.5,
            iou=0.5,
            verbose=False
        )

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes

            for box, track_id in zip(boxes.xyxy, boxes.id):

                x1, y1, x2, y2 = map(int, box.tolist())
                track_id = int(track_id)

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw ID label
                label = f"ID {track_id}"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

        # Show frame
        cv2.imshow("Tracking Debug (Press Q to exit)", frame)

        # Exit on Q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows()