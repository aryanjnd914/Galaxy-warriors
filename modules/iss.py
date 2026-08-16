import requests

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
