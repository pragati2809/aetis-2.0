from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()
 
client   = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
FROM_NUM = os.getenv("TWILIO_FROM")
POLICE   = os.getenv("POLICE_PHONE")
 
def send_sms_alert(event: dict):
    vtype = event.get("vehicle_type", "emergency vehicle")
    cam   = event.get("camera_id", "?")
    speed = event.get("speed_kmh", 0)
    dirn  = event.get("direction", "?")
    conf  = event.get("confidence", 0)
    msg = (
        f"AETIS ALERT: {vtype.upper()} detected\n"
        f"Camera: {cam} | Direction: {dirn} | Speed: {speed}km/h\n"
        f"Confidence: {conf:.0%} | Green corridor activated"
    )
    try:
        client.messages.create(body=msg, from_=FROM_NUM, to=POLICE)
        print("SMS alert sent.")
    except Exception as e:
        print(f"SMS failed (check Twilio credentials): {e}")
 
def send_road_damage_alert(event: dict):
    dtype = event.get("damage_type", "road damage")
    sev   = event.get("severity", "UNKNOWN")
    gps   = event.get("gps", (0, 0))
    msg = (
        f"AETIS ROAD ALERT: {dtype.upper()} [{sev}]\n"
        f"Camera: {event.get('camera_id','?')}\n"
        f"Maps: https://maps.google.com/?q={gps[0]},{gps[1]}"
    )
    try:
        client.messages.create(body=msg, from_=FROM_NUM, to=POLICE)
    except Exception as e:
        print(f"Road SMS failed: {e}")

