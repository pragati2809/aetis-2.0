# signal_server.py — runs on Laptop A or Laptop B
from flask import Flask, request, jsonify, render_template_string
import threading, time

app = Flask(__name__)

# Which signals this laptop is responsible for
# Laptop A handles signal_1 and signal_2
# Laptop B handles signal_3
# Change this list per laptop
MY_SIGNALS = ["signal_1", "signal_2"]   # ← change to ["signal_3"] on Laptop B

NORMAL_STATE = {
    "signal_1": "green",
    "signal_2": "red",
    "signal_3": "red",
}

# Current state held in memory
current_state = {sig: NORMAL_STATE[sig] for sig in MY_SIGNALS}

SIGNAL_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>AETIS Signal Display</title>
  <meta http-equiv="refresh" content="1">
  <style>
    body { margin:0; background:#111; display:flex; flex-direction:column;
           align-items:center; justify-content:center; height:100vh;
           font-family:sans-serif; gap:40px; }
    .signal-box { display:flex; flex-direction:column; align-items:center; gap:12px; }
    .label { color:#aaa; font-size:18px; letter-spacing:.05em; }
    .pole { background:#222; border-radius:18px; padding:20px 28px;
            display:flex; flex-direction:column; gap:18px;
            border:2px solid #333; }
    .light { width:90px; height:90px; border-radius:50%; opacity:.15;
             transition: opacity .3s, box-shadow .3s; }
    .light.on { opacity:1; }
    .red.on    { background:#e53935; box-shadow:0 0 40px #e5393588; }
    .yellow.on { background:#fdd835; box-shadow:0 0 40px #fdd83588; }
    .green.on  { background:#43a047; box-shadow:0 0 40px #43a04788; }
    .red    { background:#e53935; }
    .yellow { background:#fdd835; }
    .green  { background:#43a047; }
    .status { color:#555; font-size:13px; margin-top:20px; }
  </style>
</head>
<body>
  {% for sig_id, phase in signals.items() %}
  <div class="signal-box">
    <div class="label">{{ sig_id.replace('_',' ').upper() }}</div>
    <div class="pole">
      <div class="light red   {% if phase == 'red'    %}on{% endif %}"></div>
      <div class="light yellow{% if phase == 'yellow' %}on{% endif %}"></div>
      <div class="light green {% if phase == 'green'  %}on{% endif %}"></div>
    </div>
  </div>
  {% endfor %}
  <div class="status">AETIS Signal Controller — auto-refreshes every 1s</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(SIGNAL_PAGE, signals=current_state)

@app.route('/set', methods=['POST'])
def set_phase():
    data = request.json
    signal_id = data.get('signal_id')
    phase     = data.get('phase')
    duration  = data.get('duration', 0)

    if signal_id not in MY_SIGNALS:
        return jsonify({"error": "signal not on this laptop"}), 400
    if phase not in ('red', 'yellow', 'green'):
        return jsonify({"error": "invalid phase"}), 400

    current_state[signal_id] = phase

    if duration > 0:
        def restore():
            time.sleep(duration)
            current_state[signal_id] = NORMAL_STATE.get(signal_id, 'red')
        threading.Thread(target=restore, daemon=True).start()

    return jsonify({"ok": True, "signal": signal_id, "phase": phase})

@app.route('/corridor', methods=['POST'])
def corridor():
    corridor_plan = request.json.get('corridor', [])
    for cmd in corridor_plan:
        if cmd['signal_id'] not in MY_SIGNALS:
            continue
        def execute(c=cmd):
            time.sleep(c.get('delay_seconds', 0))
            current_state[c['signal_id']] = 'green'
            time.sleep(c.get('duration', 30))
            current_state[c['signal_id']] = NORMAL_STATE.get(c['signal_id'], 'red')
        threading.Thread(target=execute, daemon=True).start()
    return jsonify({"ok": True})

@app.route('/status')
def status():
    return jsonify(current_state)

@app.route('/reset')
def reset():
    for sig in MY_SIGNALS:
        current_state[sig] = NORMAL_STATE[sig]
    return jsonify({"ok": True})

if __name__ == '__main__':
    print(f"Signal display running — open http://localhost:5000 in browser")
    app.run(host='0.0.0.0', port=5000)