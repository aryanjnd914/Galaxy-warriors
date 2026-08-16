from flask import Flask, render_template, jsonify, send_file
from flask_socketio import SocketIO, emit
from modules.data_engine import fetch_live_tle
from modules.ml_model import score_debris
from modules.report_gen import generate_pdf
from modules.conjunction import compute_conjunctions, compute_collision_probability
from modules.ai_reports import generate_all_threat_reports
from modules.monte_carlo import run_monte_carlo
from modules.anomaly import detect_anomalies
from modules.prediction import predict_decay
from modules.sgp4_propagator import propagate_debris
from modules.mission_queue import compute_mission_queue
from modules.voice_alert import speak, announce_critical, announce_conjunction, announce_startup
import threading
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "orbitguard2026"
socketio = SocketIO(app, cors_allowed_origins="*")

print("[startup] Loading debris data...")
_debris = fetch_live_tle()
_scored = score_debris(_debris)
print(f"[startup] Scored {len(_scored)} objects")

print("[startup] Running SGP4 propagation...")
_sgp4_positions = propagate_debris(_scored)
print(f"[startup] SGP4 positions computed for {len(_sgp4_positions)} objects")

print("[startup] Running anomaly detection...")
_anomalies = detect_anomalies(_scored)
print("[startup] Anomaly detection complete")

print("[startup] Computing conjunctions...")
_conjunctions = compute_conjunctions(_scored)
print(f"[startup] {len(_conjunctions)} conjunctions found")

print("[startup] Running Monte Carlo...")
_monte_carlo = run_monte_carlo(_scored)
print("[startup] Monte Carlo done")

print("[startup] Running decay predictions...")
_predictions = predict_decay(_scored)
print("[startup] Decay predictions complete")

print("[startup] Computing AI mission queue...")
_collision_probs = compute_collision_probability(_scored)
_mission_queue = compute_mission_queue(_scored, _collision_probs, _predictions, _conjunctions)
print(f"[startup] Mission queue: {len(_mission_queue)} objects ranked")

announce_startup(len(_scored), sum(1 for d in _scored if d.get("risk_level") == "CRITICAL"))

def background_push():
    while True:
        time.sleep(5)
        try:
            positions = propagate_debris(_scored)
            socketio.emit("live_update", {
                "sgp4": positions,
                "conjunctions": _conjunctions,
                "timestamp": time.strftime("%H:%M:%S UTC")
            })
        except Exception as e:
            print(f"[socketio] Push error: {e}")

push_thread = threading.Thread(target=background_push, daemon=True)
push_thread.start()
print("[startup] WebSocket live push started every 5 seconds")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulation")
def simulation():
    return render_template("simulation.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/api-docs")
def api_docs():
    return render_template("api_docs.html")

@app.route("/report/download")
def report_download():
    debris = fetch_live_tle()
    scored = score_debris(debris)
    pdf = generate_pdf(scored)
    return send_file(pdf, download_name="orbit_guard_report.pdf", as_attachment=True, mimetype="application/pdf")

@app.route("/api/debris")
def api_debris():
    return jsonify(_scored)

@app.route("/api/risk/<norad_id>")
def api_risk(norad_id):
    obj = next((d for d in _scored if str(d.get("norad_id")) == str(norad_id)), None)
    if obj:
        return jsonify(obj)
    return jsonify({"error": f"Object {norad_id} not found"}), 404

@app.route("/api/sgp4")
def api_sgp4():
    return jsonify(_sgp4_positions)

@app.route("/api/conjunctions")
def api_conjunctions():
    return jsonify(_conjunctions)

@app.route("/api/collision_probability")
def api_collision_prob():
    return jsonify(_collision_probs)

@app.route("/api/ai_reports")
def api_ai_reports():
    reports = generate_all_threat_reports(_scored)
    return jsonify(reports)

@app.route("/api/monte_carlo")
def api_monte_carlo():
    return jsonify(_monte_carlo)

@app.route("/api/anomalies")
def api_anomalies():
    return jsonify(_anomalies)

@app.route("/api/predictions")
def api_predictions():
    return jsonify(_predictions)

@app.route("/api/mission_queue")
def api_mission_queue():
    return jsonify(_mission_queue)

@app.route("/api/voice_alert")
def api_voice_alert():
    critical = [d for d in _scored if d.get("risk_level") == "CRITICAL"]
    if critical:
        announce_critical(critical[0])
    else:
        speak("ORBIT-GUARD status nominal. No critical debris detected.")
    return jsonify({"status": "alert sent"})

@app.route("/api/voice_status")
def api_voice_status():
    speak(f"ORBIT-GUARD Mission Control. Tracking {len(_scored)} debris objects. {len(_conjunctions)} active conjunctions detected.")
    return jsonify({"status": "ok"})

@app.route("/api/voice_conjunction")
def api_voice_conjunction():
    if _conjunctions:
        c = _conjunctions[0]
        announce_conjunction(c.get("object1","OBJ-A"), c.get("object2","OBJ-B"), c.get("distance_km", 0))
    return jsonify({"status": "ok"})

@socketio.on("connect")
def on_connect():
    print("[socketio] Client connected")
    emit("live_update", {
        "sgp4": _sgp4_positions,
        "conjunctions": _conjunctions,
        "timestamp": time.strftime("%H:%M:%S UTC")
    })

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
