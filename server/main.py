from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio, json, threading, os, redis
from dotenv import load_dotenv
load_dotenv()
 
from detection.ev_detector   import EVDetector
#from detection.road_detector  import RoadDamageDetector
from hardware.signal_client   import signal_manager
from server.routing           import predict_corridor
from server.database          import log_ev_event,init_db, get_recent_ev_events
from server.alerts            import send_sms_alert
import cv2


last_detection_time = {}
COOLDOWN_SECONDS = 10  # adjust (10–20 sec recommended)


app = FastAPI(title="AETIS")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
 
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
 
# Dashboard WebSocket clients
dashboard_clients: list[WebSocket] = []
 
ev_detector   = None  # loaded after model files exist
#road_detector = None
 
CAMERA_GPS = {1: (28.5355, 77.3910), 2: (28.5370, 77.3925)}
 
# ─── Dashboard WebSocket ──────────────────────────────────────────────────────
 
async def broadcast_dashboard(msg: dict):
    dead = []
    for ws in dashboard_clients:
        try:
            await ws.send_text(json.dumps(msg))
        except Exception:
            dead.append(ws)
    for ws in dead:
        dashboard_clients.remove(ws)
 
@app.websocket("/ws")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    dashboard_clients.append(ws)
    # Send recent history on connect
    try:
        events = get_recent_ev_events(10)
        for e in events:
            await ws.send_text(json.dumps({"type": "ev_history", "data": str(e)}))
    except Exception:
        pass
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        dashboard_clients.remove(ws)
 
# ─── Signal Display WebSocket ─────────────────────────────────────────────────
 
@app.websocket("/ws/signal/{signal_id}")
async def ws_signal(ws: WebSocket, signal_id: str):
    await signal_manager.connect(signal_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        signal_manager.disconnect(signal_id, ws)
 
# ─── REST endpoints ───────────────────────────────────────────────────────────
 
@app.get("/")
def root():
    return {"status": "AETIS running"}
 
@app.get("/status")
def get_status():
    return {
        "status": "running",
        "dashboard_clients": len(dashboard_clients),
        "signal_states": signal_manager.get_status(),
    }
 
@app.get("/reset")
async def reset_signals():
    await signal_manager.reset_all()
    return {"ok": True, "message": "All signals reset to RED"}
 
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open("dashboard/index.html", encoding="utf-8") as f:
        return f.read()
    
@app.get("/signal/{signal_id}", response_class=HTMLResponse)
async def serve_signal_page(signal_id: str):
    with open("dashboard/signal.html", encoding="utf-8") as f:
        html = f.read().replace("{{SIGNAL_ID}}", signal_id)
        return html
 
# ─── Event Handlers ───────────────────────────────────────────────────────────
 
#async def handle_ev_detection(event: dict):
    """print(f"EV detected: {event['vehicle_type']} cam {event['camera_id']}")
    corridor = predict_corridor(event)
    if corridor:
        await signal_manager.activate_green_corridor(corridor)
        event["corridor"] = corridor
    log_ev_event(event)
    send_sms_alert(event)
    await broadcast_dashboard({"type": "ev_detection", "data": event})"""
import time

async def handle_ev_detection(event: dict):
    cam_id = event["camera_id"]
    current_time = time.time()

    # Check cooldown
    if cam_id in last_detection_time:
        if current_time - last_detection_time[cam_id] < COOLDOWN_SECONDS:
            return

    # Update last detection time
    last_detection_time[cam_id] = current_time

    print(f"🚑 EV detected: {event['vehicle_type']} cam {cam_id}")

    corridor = [{"signal_id": "signal_1"}]
    if corridor:
        await signal_manager.activate_green_corridor(corridor)
        event["corridor"] = corridor

    log_ev_event(event)
    send_sms_alert(event)
    await broadcast_dashboard({"type": "ev_detection", "data": event})
    print("🔥 EV EVENT TRIGGERED", event)
 
async def handle_road_damage(event: dict):
    #log_road_damage(event)
    await broadcast_dashboard({"type": "road_damage", "data": event})
 
# ─── Background threads ───────────────────────────────────────────────────────
 
def redis_listener():
    """Background thread: subscribe to Redis channels from detectors."""
    pubsub = r.pubsub()
    pubsub.subscribe("ev_detections")
    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        channel = message["channel"].decode()
        data    = json.loads(message["data"])
        loop    = asyncio.new_event_loop()
        if channel == "ev_detections":
            loop.run_until_complete(handle_ev_detection(data))
        """elif channel == "road_damage":
            loop.run_until_complete(handle_road_damage(data))"""
        loop.close()
 
def camera_loop():
    """Main camera capture and detection loop."""
    global ev_detector
    if ev_detector is None :
        print("Models not loaded yet — camera loop skipped.")
        #return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera failed to open!")
        return
    else:
        print("✅ Camera opened successfully!")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("AETIS Camera Feed", frame)  # ADD THIS
        if cv2.waitKey(1) & 0xFF == ord('q'):   # press Q to quit
            break
        frame_count += 1
        #ev_detector.detect(frame, camera_id=1)
        if ev_detector:
            ev_detector.detect(frame, camera_id=1)

       
        """if frame_count % 6 == 0:
            road_detector.detect(frame, camera_id=1,
                                 camera_gps=CAMERA_GPS[1])"""
 
@app.on_event("startup")
async def startup():
    global ev_detector
    #init_db()
    # Load models if they exist
    ev_path   = "models/ev_best.pt"
    #road_path = "models/road_best.pt"
    if os.path.exists(ev_path):
        ev_detector = EVDetector(ev_path)
    else:
        print(f"WARNING: {ev_path} not found — add model after training")
    """if os.path.exists(road_path):
        road_detector = RoadDamageDetector(road_path)
    else:
        print(f"WARNING: {road_path} not found — add model after training")"""
    # Start background threads
    threading.Thread(target=redis_listener, daemon=True).start()
    #if ev_detector :
    threading.Thread(target=camera_loop, daemon=True).start()
    print("AETIS server started.")
    print("Dashboard:     http://localhost:8000/dashboard")
    print("Signal A page: http://localhost:8000/signal/signal_1")
    print("Signal B page: http://localhost:8000/signal/signal_2")
