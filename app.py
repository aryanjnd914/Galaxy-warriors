from flask import Flask, render_template, jsonify, send_file
from modules.data_engine import fetch_live_tle
from modules.ml_model import score_debris
from modules.report_gen import generate_pdf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/report/download')
def report_download():
    debris = fetch_live_tle()
    scored = score_debris(debris)
    pdf = generate_pdf(scored)
    return send_file(pdf, download_name='orbit_guard_report.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/api/debris')
def api_debris():
    debris = fetch_live_tle()
    scored = score_debris(debris)
    return jsonify(scored)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
