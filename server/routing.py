# server/routing.py
import math
 
# GPS coordinates of each camera (measure yours with Google Maps)
CAMERA_GPS = {
    1: (28.5355, 77.3910),   # your camera 1 location
    2: (28.5370, 77.3925),   # your camera 2 location
}
 
# GPS coordinates of each signal junction
SIGNAL_GPS = {
    "signal_1": (28.5362, 77.3918),
    "signal_2": (28.5375, 77.3930),
    "signal_3": (28.5390, 77.3945),
}
 
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
 
def predict_corridor(detection_event: dict) -> list:
    cam_id    = detection_event["camera_id"]
    direction = detection_event.get("direction", "north")
    speed_kmh = detection_event.get("speed_kmh", 40) or 40
    speed_ms  = speed_kmh / 3.6
 
    cam_gps = CAMERA_GPS.get(cam_id)
    if not cam_gps:
        return []
 
    corridor = []
    for sig_id, sig_gps in SIGNAL_GPS.items():
        dlat = sig_gps[0] - cam_gps[0]
        dlon = sig_gps[1] - cam_gps[1]
        # Only include signals in the direction of travel
        in_dir = (
            (direction == "north" and dlat > 0.0005) or
            (direction == "south" and dlat < -0.0005) or
            (direction == "east"  and dlon > 0.0005) or
            (direction == "west"  and dlon < -0.0005)
        )
        if not in_dir:
            continue
 
        dist_m   = haversine(*cam_gps, *sig_gps)
        eta_sec  = dist_m / speed_ms
        green_at = max(0, eta_sec - 3)   # turn green 3s before arrival
 
        corridor.append({
            "signal_id":      sig_id,
            "delay_seconds":  round(green_at, 1),
            "duration":       18,
            "eta_seconds":    round(eta_sec, 1),
            "distance_m":     round(dist_m),
        })
 
    corridor.sort(key=lambda x: x["delay_seconds"])
    return corridor
