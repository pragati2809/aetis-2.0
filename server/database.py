import psycopg2, os, json
from dotenv import load_dotenv
load_dotenv()
 
DB_URL = os.getenv("POSTGRES_URL")
 
def get_conn():
    return psycopg2.connect(DB_URL)
 
def init_db():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ev_events (
            id           SERIAL PRIMARY KEY,
            camera_id    INTEGER,
            vehicle_type VARCHAR(50),
            confidence   FLOAT,
            direction    VARCHAR(20),
            speed_kmh    FLOAT,
            corridor     JSONB,
            detected_at  TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS road_damage (
            id           SERIAL PRIMARY KEY,
            camera_id    INTEGER,
            damage_type  VARCHAR(50),
            severity     VARCHAR(10),
            confidence   FLOAT,
            gps_lat      FLOAT,
            gps_lon      FLOAT,
            reported_at  TIMESTAMP DEFAULT NOW(),
            repaired     BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit(); conn.close()
    print("Database tables ready.")
 
def log_ev_event(event: dict):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO ev_events
              (camera_id,vehicle_type,confidence,direction,speed_kmh,corridor)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (event['camera_id'], event['vehicle_type'], event['confidence'],
              event.get('direction'), event.get('speed_kmh'),
              json.dumps(event.get('corridor', []))))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"DB log error: {e}")
 
def log_road_damage(event: dict):
    try:
        conn = get_conn(); cur = conn.cursor()
        gps = event.get('gps', (0, 0))
        cur.execute("""
            INSERT INTO road_damage
              (camera_id,damage_type,severity,confidence,gps_lat,gps_lon)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (event['camera_id'], event['damage_type'], event['severity'],
              event['confidence'], gps[0], gps[1]))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"DB log error: {e}")
 
def get_recent_ev_events(limit=20):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM ev_events ORDER BY detected_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall(); conn.close()
    return rows
 
def get_road_damage_report():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM road_damage WHERE repaired=FALSE ORDER BY reported_at DESC")
    rows = cur.fetchall(); conn.close()
    return rows
