content = '''from flask import Flask, render_template, jsonify, send_file
from modules.data_engine import fetch_live_tle
from modules.ml_model import score_debris
from modules.report_gen import generate_pdf
from modules.conjunction import compute_conjunctions, compute_collision_probability
from modules.ai_reports import generate_all_threat_reports
from modules.monte_carlo import run_monte_carlo
from modules.anomaly import detect_anomalies
from modules.prediction import predict_decay

app = Flask(__name__)

print("[startup] Loading debris data...")
_debris = fetch_live_tle()
_scored = score_debris(_debris)
print(f"[startup] Scored {len(_scored)} objects")

print("[startup] Running anomaly detection...")
_anomalies = detect_anomalies(_scored)
print("[startup] Anomaly detection complete")

print("[startup] Computing conjunctions...")
_conjunctions = compute_conjunctions(_scored)
print(f"[startup] {len(_conjunctions)} conjunctions found")

print("[startup] Running Monte Carlo...")
_monte = run_monte_carlo(_scored)
print("[startup] Monte Carlo done")

print("[startup] Running decay predictions...")
_predictions = predict_decay(_scored)
print("[startup] Decay predictions complete")

_collision_probs = compute_collision_probability(_scored)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulation")
def simulation():
    return render_template("simulation.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/report/download")
def report_download():
    pdf = generate_pdf(_scored)
    return send_file(pdf, download_name="orbit_guard_report.pdf", as_attachment=True, mimetype="application/pdf")

@app.route("/api/debris")
def api_debris():
    return jsonify(_scored)

@app.route("/api/anomalies")
def api_anomalies():
    return jsonify(_anomalies)

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
    return jsonify(_monte)

@app.route("/api/predictions")
def api_predictions():
    return jsonify(_predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py written successfully")