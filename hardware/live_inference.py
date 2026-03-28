# live_inference.py — put this in your aetis/ root folder
# Usage: python live_inference.py

import cv2
from ultralytics import YOLO

ev_model   = YOLO('models/ev_best.pt')
road_model = YOLO('models/road_best.pt')

EV_CLASSES   = {0: 'ambulance', 1: 'fire_truck'}
ROAD_CLASSES = {0: 'pothole',   1: 'crack',      2: 'broken_road'}

def annotate(frame):
    out = frame.copy()

    for box in ev_model(frame, conf=0.5, verbose=False)[0].boxes:
        cls  = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
        label = f"{EV_CLASSES.get(cls,'?')} {conf:.0%}"
        cv2.rectangle(out, (x1,y1), (x2,y2), (0,200,0), 3)
        cv2.putText(out, label, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,200,0), 2)

    for box in road_model(frame, conf=0.5, verbose=False)[0].boxes:
        cls  = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
        label = f"{ROAD_CLASSES.get(cls,'?')} {conf:.0%}"
        cv2.rectangle(out, (x1,y1), (x2,y2), (0,100,255), 3)
        cv2.putText(out, label, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)

    return out

cap = cv2.VideoCapture(0)   # change to 1 or 2 if wrong camera
print("Live camera open. Press S to run inference, Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show plain live feed (fast — no inference every frame)
    cv2.putText(frame, "Press S to analyse | Q to quit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.imshow("AETIS Live", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        print("Running inference...")
        result = annotate(frame)
        cv2.imshow("AETIS Live", result)   # shows result in same window
        cv2.imwrite("inference_result.jpg", result)
        print("Done — result saved to inference_result.jpg")
        cv2.waitKey(0)   # freeze on result until any key pressed

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()