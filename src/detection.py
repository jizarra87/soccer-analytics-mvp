from ultralytics import YOLO
import cv2

# Load YOLO model (pretrained)
model = YOLO("yolov8n.pt")  # lightweight model


def detect_players(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection
        results = model(frame)

        # Draw results
        annotated_frame = results[0].plot()

        cv2.imshow("Player Detection", annotated_frame)

        # Press q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()