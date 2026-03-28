# detection/ev_detector.py
from ultralytics import YOLO
import redis, json, os, time, cv2
from dotenv import load_dotenv
load_dotenv()
 
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
 
class EVDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.conf  = float(os.getenv("CONFIDENCE_EV", 0.85))
        self.prev_positions = {}   # for speed estimation
        self.prev_times     = {}
        print(f"EV detector loaded: {model_path}")
 
    def estimate_speed(self, bbox, camera_id, frame_h):
        """Rough speed estimate from bounding box size change over time."""
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        now = time.time()
        if camera_id in self.prev_positions:
            prev_cx, prev_cy = self.prev_positions[camera_id]
            dt = now - self.prev_times[camera_id]
            pixel_dist = ((cx - prev_cx)**2 + (cy - prev_cy)**2)**0.5
            # rough conversion: assume 1 pixel ~= 0.1 metres at typical camera mount
            speed_kmh = (pixel_dist * 0.1 / dt) * 3.6 if dt > 0 else 0
        else:
            speed_kmh = 0
        self.prev_positions[camera_id] = (cx, cy)
        self.prev_times[camera_id]     = now
        return round(min(speed_kmh, 120), 1)
 
    def estimate_direction(self, bbox, frame_w, frame_h):
        """Guess direction from position in frame."""
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        if cx < frame_w * 0.4:  return "west"
        if cx > frame_w * 0.6:  return "east"
        if cy < frame_h * 0.4:  return "north"
        return "south"
 
    def detect(self, frame, camera_id: int):
        h, w = frame.shape[:2]
        results = self.model(frame, conf=self.conf, verbose=False)[0]
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label  = self.model.names[cls_id]
            if label not in ("ambulance", "fire_truck", "police_vehicle"):
                continue
            bbox  = box.xyxy[0].tolist()
            conf  = float(box.conf[0])
            speed = self.estimate_speed(bbox, camera_id, h)
            dirn  = self.estimate_direction(bbox, w, h)
            event = {
                "camera_id":    camera_id,
                "vehicle_type": label,
                "confidence":   round(conf, 3),
                "direction":    dirn,
                "speed_kmh":    speed,
                "bbox":         [round(x) for x in bbox],
            }
            r.publish("ev_detections", json.dumps(event))
            print(f"ALERT: {label} on cam {camera_id} → {dirn} @ {speed}km/h")
