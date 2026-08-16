# Create ISS module
iss_module = '''import requests

ISS_URL = "http://api.open-notify.org/iss-now.json"

def get_iss_position():
    """Fetch live ISS position from open-notify API."""
    try:
        resp = requests.get(ISS_URL, timeout=5)
        data = resp.json()
        if data.get("message") == "success":
            pos = data["iss_position"]
            return {
                "name": "ISS (ZARYA)",
                "norad_id": "25544",
                "latitude": float(pos["latitude"]),
                "longitude": float(pos["longitude"]),
                "altitude_km": 408.0,
                "type": "station",
                "timestamp": data["timestamp"]
            }
    except Exception as e:
        print(f"[ISS] Failed to fetch position: {e}")
    return {
        "name": "ISS (ZARYA)",
        "norad_id": "25544",
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude_km": 408.0,
        "type": "station",
        "timestamp": 0
    }
'''

with open('modules/iss.py', 'w', encoding='utf-8') as f:
    f.write(iss_module)
print("modules/iss.py created")

# Update app.py to add ISS route
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

iss_import = "from modules.iss import get_iss_position\n"
iss_route = '''
@app.route("/api/iss")
def api_iss():
    return jsonify(get_iss_position())
'''

if 'from modules.iss' not in app_content:
    app_content = iss_import + app_content
if '/api/iss' not in app_content:
    app_content = app_content.replace(
        'if __name__ == "__main__":',
        iss_route + '\nif __name__ == "__main__":'
    )
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("app.py updated with ISS route")