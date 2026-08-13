import requests, json, os
from datetime import datetime, timedelta

CACHE_FILE = "data/cached_debris_tle.json"

# CelesTrak GP API — open JSON endpoint, no auth needed
GP_URL = "https://celestrak.org/SOCRATES/query.php?CODE=ALL&MAX=100&DAYS=7&TYPE=p&FORMAT=json"
GP_DEBRIS_URL = "https://celestrak.org/GP/query?GROUP=debris&FORMAT=json"
GP_IRIDIUM_URL = "https://celestrak.org/GP/query?SPECIAL=iridium-33-debris&FORMAT=json"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OrbitGuard/1.0; student research)"}

def fetch_live_tle():
    if os.path.exists(CACHE_FILE):
        mtime = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        if datetime.now() - mtime < timedelta(hours=1):
            print("[data_engine] Using cached TLE data")
            with open(CACHE_FILE) as f:
                return json.load(f)

    # Try GP JSON API
    try:
        print("[data_engine] Trying CelesTrak GP JSON API...")
        resp = requests.get(GP_DEBRIS_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        gp_data = resp.json()
        print(f"[data_engine] GP API returned {len(gp_data)} objects")

        debris_list = []
        for obj in gp_data[:100]:
            debris_list.append({
                "name": obj.get("OBJECT_NAME", "UNKNOWN DEB"),
                "norad_id": str(obj.get("NORAD_CAT_ID", "00000")),
                "epoch": obj.get("EPOCH", ""),
                "inclination": float(obj.get("INCLINATION", 0)),
                "eccentricity": float(obj.get("ECCENTRICITY", 0)),
                "mean_motion": float(obj.get("MEAN_MOTION", 0)),
                "perigee": float(obj.get("PERIGEE", 400)),
                "apogee": float(obj.get("APOGEE", 500)),
                "bstar": float(obj.get("BSTAR", 0)),
                "raan": float(obj.get("RA_OF_ASC_NODE", 0)),
                "tle_line1": obj.get("TLE_LINE1", ""),
                "tle_line2": obj.get("TLE_LINE2", ""),
            })

        os.makedirs("data", exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(debris_list, f, indent=2)
        print(f"[data_engine] Saved {len(debris_list)} debris objects")
        return debris_list

    except Exception as e:
        print(f"[data_engine] GP API failed: {e} — using fallback")
        return _fallback_data()

def _fallback_data():
    fallback = [
        {"name": "FENGYUN 1C DEB", "norad_id": "29228", "inclination": 98.6, "eccentricity": 0.001, "mean_motion": 14.2, "perigee": 790, "apogee": 810, "bstar": 0.0001, "raan": 100.0, "tle_line1": "", "tle_line2": ""},
        {"name": "IRIDIUM 33 DEB", "norad_id": "33778", "inclination": 86.4, "eccentricity": 0.002, "mean_motion": 14.34, "perigee": 760, "apogee": 790, "bstar": 0.0002, "raan": 200.0, "tle_line1": "", "tle_line2": ""},
        {"name": "COSMOS 2251 DEB", "norad_id": "34454", "inclination": 74.0, "eccentricity": 0.0015, "mean_motion": 14.28, "perigee": 770, "apogee": 800, "bstar": 0.00015, "raan": 150.0, "tle_line1": "", "tle_line2": ""},
        {"name": "SL-16 R/B", "norad_id": "22285", "inclination": 71.0, "eccentricity": 0.0005, "mean_motion": 14.15, "perigee": 820, "apogee": 840, "bstar": 0.00005, "raan": 180.0, "tle_line1": "", "tle_line2": ""},
        {"name": "CZ-4B R/B", "norad_id": "27601", "inclination": 98.0, "eccentricity": 0.0008, "mean_motion": 14.22, "perigee": 780, "apogee": 800, "bstar": 0.00008, "raan": 120.0, "tle_line1": "", "tle_line2": ""},
        {"name": "BREEZE-M DEB", "norad_id": "39915", "inclination": 49.0, "eccentricity": 0.003, "mean_motion": 13.9, "perigee": 400, "apogee": 900, "bstar": 0.0003, "raan": 90.0, "tle_line1": "", "tle_line2": ""},
        {"name": "THOR AGENA DEB", "norad_id": "01642", "inclination": 99.1, "eccentricity": 0.001, "mean_motion": 14.5, "perigee": 700, "apogee": 720, "bstar": 0.0001, "raan": 45.0, "tle_line1": "", "tle_line2": ""},
        {"name": "DELTA 1 DEB", "norad_id": "06187", "inclination": 90.1, "eccentricity": 0.002, "mean_motion": 14.1, "perigee": 840, "apogee": 870, "bstar": 0.00012, "raan": 270.0, "tle_line1": "", "tle_line2": ""},
    ]
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(fallback, f, indent=2)
    return fallback
