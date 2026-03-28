# detection/road_detector.py
from ultralytics import YOLO
import redis, json, os
from dotenv import load_dotenv
load_dotenv()
 
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
 
SEVERITY_MAP = {
    "pothole":       "HIGH",
    "crack":         "MEDIUM",
    "broken_road":   "HIGH",
    "rutting":       "MEDIUM",
    "patched_road":  "LOW",
}

class RoadDamageDetector:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.conf  = float(os.getenv("CONFIDENCE_ROAD", 0.70))
        self.last_log = {}  # prevent duplicate logs within 30 seconds
        print(f"Road detector loaded: {model_path}")
 
    def detect(self, frame, camera_id: int, camera_gps: tuple):
        results = self.model(frame, conf=self.conf, verbose=False)[0]
        for box in results.boxes:
            cls_id    = int(box.cls[0])
            label     = self.model.names[cls_id]
            conf      = float(box.conf[0])
            severity  = SEVERITY_MAP.get(label, "MEDIUM")
 
            # Deduplicate: don't log same camera+type within 30s
            key = f"{camera_id}_{label}"
            import time
            now = time.time()
            if now - self.last_log.get(key, 0) < 30:
                continue
            self.last_log[key] = now
 
            event = {
                "camera_id":   camera_id,
                "damage_type": label,
                "severity":    severity,
                "confidence":  round(conf, 3),
                "gps":         list(camera_gps),
            }
            r.publish("road_damage", json.dumps(event))
            print(f"Road damage: {label} [{severity}] at cam {camera_id}")
